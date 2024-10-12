import boto3
import json
import requests
import os
import datetime
from dotenv import load_dotenv

load_dotenv()
refresh_token = os.getenv('refresh_token_tg')
refresh_token = os.getenv('refresh_token_yd')

base_url = "https://public-services.clarifruit.com"

headers = {"Token": refresh_token}
import_headers = {'X-Api-Key': refresh_token, 'Content-Type': 'application/json'}
two_weeks_ago = datetime.datetime.now() - datetime.timedelta(weeks=1)
two_weeks_ago_timestamp = int(two_weeks_ago.timestamp() * 1000)
# numberOfDays = 12
numberOfDays = input("Number of Days you want to exports inspections: ")
company_id_source = input("Company ID of the source company: ")
company_id_destination = input("Company ID of the destination company: ")


def init():
    print("Starting handler")
    result = get_inspections(company_id_source)
    print('got all inspections, about to iterate them, count:' + str(len(result)))
    # iterate_inspections(result, company_id_source)
    print("Finished handler")

def get_inspections(company_id):
    start_pos = 0
    response = None
    inspections = []
    # while response is None or (response.json()['inspections'].__len__()) > 0:
    response = requests.get(base_url + f"/api/export?fromPeriod={numberOfDays}d&companyId=" + str(company_id), headers=headers)
    response.raise_for_status()
    inspections = inspections + response.json()['inspections']
    # start_pos += 50
    print(response.json()['inspections'].__len__())
    save_json_to_file(inspections,"inspections_archived.json")

    return inspections


def iterate_inspections(result, company_id):
    inspectionToBeDeleted = []
    for i in result:
        id_ = i["id"]
        inspectionToBeDeleted.append(id_)
        print(id_)
        # delete_inspection(id_)
    print(inspectionToBeDeleted)
    print(len(inspectionToBeDeleted))
    import_inspections(company_id)

def import_inspections(company_id):
    print("Starting import process")
    json_folder = 'inspections_to_import'
    for json_file in os.listdir(json_folder):
        # Only process JSON files
        if json_file.endswith('.json'):
            # Read the JSON data from the file
            with open(os.path.join(json_folder, json_file)) as json_data:
                json_data = json.load(json_data)
                file_name = json_file
                if "_b1" in file_name or "failed" in file_name or "_b" in file_name:
                    # manipulate json data
            ##        json_data[0]["creationTime"] = int(two_weeks_ago_timestamp)
                    print("Special json file")
                    # with open("file.json", "w") as json_file:
                    #     json.dump(json_data, json_file)

                # Perform POST request for current JSON file
                # TODO response = requests.post(base_url + '/api/import?companyId=' + company_id, json=json_data,headers=import_headers)
                response.raise_for_status()
                print(json_file, 'was imported successfully', response.text)
                
def http_get(bearer_token, url):
    r = requests.get(url=url, headers={"Authorization": bearer_token})
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        print(f"failed with error code: {str(r.status_code)}. url: {url}")
        return None


def http_post(bearer_token, url, body=None):
    if body is not None:
        r = requests.post(url=url, headers={"Authorization": bearer_token}, json=body)
    else:
        r = requests.post(url=url, headers={"Authorization": bearer_token})
    # print(r.status_code)
    # return json.loads(r.text)

# Function to save JSON data to a file without overwriting
def save_json_to_file(data, file_name):
    base_name, extension = os.path.splitext(file_name)  # Split the file name and extension
    counter = 1
    
    # Check if file exists and modify the name if necessary
    while os.path.exists(file_name):
        file_name = f"{base_name}_{counter}{extension}"
        counter += 1

    # Save the JSON data to the new file
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {file_name}")



init()