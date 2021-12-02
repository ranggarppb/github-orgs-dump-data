import requests
import sqlalchemy
from sqlalchemy import text
import os

org_api_url = f"https://api.github.com/orgs/{os.environ.get('ORG_NAME')}"
user_api_url = 'https://api.github.com/users'
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASS')
db_name = os.environ.get('DB_NAME')
db_socket_dir = '/cloudsql'
instance_connection_name = os.environ.get('DB_CONNECTION_NAME')

pool = sqlalchemy.create_engine(f'postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?host={db_socket_dir}/{instance_connection_name}')

def filter_field(response, fields):
  return [
    {
      key: item[key] for key in fields
    } for item in response
  ]

def get_members():
    members = requests.get(
        f"{org_api_url}/members", 
        headers={
        "Accept":"application/vnd.github.v3+json",
        }
    )
    if members.status_code == 200:
        members = filter_field(members.json(), ['login', 'id', 'avatar_url'])
        return members
    else:
        return "Error in calling api"

def get_user_connection(login, connection_type):
    connection = requests.get(
        f"{user_api_url}/{login}/{connection_type}", 
        headers={
        "Accept":"application/vnd.github.v3+json",
        }
    )

    if connection.status_code == 200:
        cnt_connection = len(connection.json())
        return cnt_connection
    else:
        return "Error in calling api"
      
def get_members_data():
  members = get_members()
  cnt_followers = [get_user_connection(x['login'], "followers") for x in members]
  cnt_following = [get_user_connection(x['login'], "following") for x in members]
  for i, member in enumerate(members):
    member['cnt_followers'] = cnt_followers[i]
    member['cnt_following'] = cnt_following[i]
  return members

def insert_members_data(member):
    with pool.connect() as conn:
        statement = text("""
            INSERT INTO member(login_id, login, avatar_url, cnt_followers, cnt_following)
            VALUES (:id, :login, :avatar_url, :cnt_followers, :cnt_following)
            ON CONFLICT (login_id) DO UPDATE
            SET login = :login, avatar_url = :avatar_url, cnt_followers = :cnt_followers, cnt_following = :cnt_following
        """)
        conn.execute(statement, **member)

def dump_members_data(request):
    members = get_members_data()
    for member in members:
        insert_members_data(member)