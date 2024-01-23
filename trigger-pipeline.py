import requests
import random
import string
import datetime
import time
import os

# generate a random id
run_identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))

# filter runs that were created after this date minus 5 minutes
delta_time = datetime.timedelta(minutes=5)
run_date_filter = (datetime.datetime.utcnow()-delta_time).strftime("%Y-%m-%dT%H:%M") 

WORKFLOW_ID = "build-image.yml"
OWNER = "realexcel2021" # replace this with your github repo username
REPO = "automation-task" # replace this with your the repo name <if you forked the repo you can leave it out>
BRANCH = 'master' # branch name for the workflow
ACTION = 'build-image.yml' # name of the yml file for github actions <if oyu forked the repo you can leave it out>

# trigger a workflow dispatch
GHA_API = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_ID}/dispatches"
GHA_API_TOKEN = os.environ["GHA_API_TOKEN"] #""
GHA_OBJ = {
    "ref":"master",
    "inputs": {
        "id": run_identifier
    }
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {GHA_API_TOKEN}'
}

# trigger workflow dispatch
trigger_build = requests.post(GHA_API, json=GHA_OBJ, headers=headers)

print(f"dispatch workflow status: {trigger_build.text} | workflow identifier: {run_identifier}")

def getjobID(response_id):
    if response_id == 204:

        print("The workflow dispatch got triggered successfully")
        # Get the status of the previous run

        workflow_id = ""

        while workflow_id == "":

            # get all the workflow runs created 5 mins ago from current time
            
            r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?created=%3E{run_date_filter}",
                headers = headers) 
            

            runs = r.json()["workflow_runs"]

            if len(runs) > 0:
                #  get job url of all recent jobs 5 mins ago
                for workflow in runs:
                    jobs_url = workflow["jobs_url"]
                    print(f"get jobs_url {jobs_url}")

                    r = requests.get(jobs_url, headers= headers)
                    
                    # pick the most recent job

                    jobs = r.json()["jobs"]
                    if len(jobs) > 0:
                        # we only take the first job because it is the most recent job
                        job = jobs[0]
                        steps = job["steps"]
                        if len(steps) >= 2:
                            second_step = steps[1] # pick the job step with the identifier
                            if second_step["name"] == run_identifier:
                                workflow_id = job["run_id"]
                        else:
                            print("waiting for steps to be executed...") # if first two steps are not finished, sleep 3 sec and come back
                            time.sleep(3)
                    else:
                        print("waiting for jobs to popup...") # if job isn't created wait for it 3secs and come back
                        time.sleep(3)
            else:
                print("waiting for workflows to popup...") # if the workflow isn't created, wait 3secs and come back
                time.sleep(3)

        return workflow_id

    else:
        print("Build didn't get triggered")


# Get dockerhub image digest

def getImageUrl():

    # request todockerhub api
    DOCKER_ACCESS_TOKEN = os.environ["DOCKER_ACCESS_TOKEN"] #"dckr_pat_F6lBFiy6gjJxKX7s7vg14eU3Zpc"
    namespace = "sheriffexcel"
    repository = "vite-app"
    api_url = f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags"
    api_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {DOCKER_ACCESS_TOKEN}'
    }

    # get dockerhub's response data
    request = requests.get(api_url, headers=api_headers)
    images = request.json()["results"]

    if request.status_code == 200:

        print(f"Dockerhub's api responded with a status code of {request.status_code}")

        # get first image in the list which is the most recent that was built
        image_digest = images[0]["digest"]
        image_name = images[0]["name"]

        print(image_name)
        image_artifact_url = f"https://hub.docker.com/layers/{namespace}/{repository}/{image_name}/images/{image_digest}"
        return image_artifact_url
    else:
        print("Request to dockerhub api failed")







job_id = getjobID(trigger_build.status_code)

job_status = ""

print(f"The new job id is {job_id}")
if job_id:
  
  # enter a loop to confirm if the job got triggered
  while job_status == "":

    # check status of the workflow dispatch job that was triggered earlier
    r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{job_id}")

    run_details = r.json()["status"]

    # check if the triggered workflow got completed successfully
    if run_details == "completed":
        print(f"The pipeline trigger got completed successfully with id of {job_id}")
        job_status = "Success"
        image_artifact = getImageUrl()
        print(f"Image Artifact Url: {image_artifact}")
        break
    elif run_details == "failure":
        print("Workflow failed")
        job_status = "Failure"
        break
    else:
        print("Workflow in progress please wait...")
        time.sleep(5)
else:
    print("Workflow didn't get triggered")





