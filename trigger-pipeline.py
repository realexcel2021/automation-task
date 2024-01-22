import requests
import random
import string
import datetime
import time

# generate a random id
run_identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))

# filter runs that were created after this date minus 5 minutes
delta_time = datetime.timedelta(minutes=5)
run_date_filter = (datetime.datetime.utcnow()-delta_time).strftime("%Y-%m-%dT%H:%M") 

WORKFLOW_ID = "build-image.yml"
OWNER = "realexcel2021"
REPO = "automation-task"
BRANCH = 'main'
ACTION = 'build-image.yml'

# trigger a workflow dispatch
GHA_API = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_ID}/dispatches"
GHA_API_TOKEN = "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"
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

print(f"dispatch workflow status: {trigger_build.status_code} | workflow identifier: {run_identifier}")

def checkJobStatus(response_id):
    if response_id == 204:

        print("The workflow dispatch got triggered successfully")
        # Get the status of the previous run
       
 

        req_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_ID}/runs"
        req_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GHA_API_TOKEN}'
        }

        workflow_id = ""

        while workflow_id == "":
                
            r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/actions/runs?created=%3E{run_date_filter}",
                headers = authHeader)
            runs = r.json()["workflow_runs"]

            if len(runs) > 0:
                for workflow in runs:
                    jobs_url = workflow["jobs_url"]
                    print(f"get jobs_url {jobs_url}")

                    r = requests.get(jobs_url, headers= authHeader)
                    
                    jobs = r.json()["jobs"]
                    if len(jobs) > 0:
                        # we only take the first job, edit this if you need multiple jobs
                        job = jobs[0]
                        steps = job["steps"]
                        if len(steps) >= 2:
                            second_step = steps[1] # if you have position the run_identifier step at 1st position
                            if second_step["name"] == run_identifier:
                                workflow_id = job["run_id"]
                        else:
                            print("waiting for steps to be executed...")
                            time.sleep(3)
                    else:
                        print("waiting for jobs to popup...")
                        time.sleep(3)
            else:
                print("waiting for workflows to popup...")
                time.sleep(3)

        print(f"workflow_id: {workflow_id}")

    else:
        print("Build didn't get triggered")

checkJobStatus(trigger_build.status_code)

