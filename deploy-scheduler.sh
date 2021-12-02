CLOUD_FUNCTION_URI=echo 
gcloud scheduler jobs create http dump-members \
    --schedule="0 */2 * * *" \
    --uri=$(yq e '.CLOUD_FUNCTION_URI' .env.yaml)