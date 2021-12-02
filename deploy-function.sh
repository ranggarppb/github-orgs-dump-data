gcloud functions deploy dump-members-data \
    --runtime python37 \
    --trigger-http \
    --entry-point dump_members_data \
    --allow-unauthenticated \
    --region asia-southeast2 \
    --env-vars-file=.env.yaml