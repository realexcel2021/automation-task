PROJECT_ID=$(gcloud config get-value core/project --quiet)
TRIGGER_ID=$1
curl -s -XDELETE -H"Authorization: Bearer $(gcloud config config-helper --format='value(credential.access_token)')" https://cloudbuild.googleapis.com/v1/projects/${PROJECT_ID}/triggers/${TRIGGER_ID} | jq '.'
view -d "{
  "description": "A sample build trigger",
  "substitutions": {
    "_TAG": "sample",
    "_DOCKERFILE": "docker/Dockerfile",
    "_MAJOR": "1",
    "_MINOR": "0",

  },
  "ignoredFiles": [
    ".gitignore",
    ".dockerignore"
  ],
  "filename": "cloudbuild.yaml"
}"

