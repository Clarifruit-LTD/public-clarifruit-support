import boto3
import json
import requests
import os
import datetime

PARAM_STORE_NAME = "/serverless/sales/demo/api_test_demosales/refreshToken"
# refresh_token = ssm.get_parameter(Name=PARAM_STORE_NAME, WithDecryption=True)['Parameter']['Value']
refresh_token = "E64TegaVlNTUBz1mKvMcUOcmjCJgnmU9PSEQTFJCi0unO"
DO_NOT_ERASE = ["65e6d83e5b71935aad28cc1e","65e73cfa0472974cb8e6b0a6","65e73c3f0472974cb8e6b0a2","65e73c700472974cb8e6b0a3"] #list of inspections that should not be erased!

base_url = "https://public-services.clarifruit.com"
# base_url = "https://services-dev.clarifruit.com"

headers = {"Token": refresh_token}
import_headers = {'X-Api-Key': refresh_token, 'Content-Type': 'application/json'}
two_weeks_ago = datetime.datetime.now() - datetime.timedelta(weeks=2)
two_weeks_ago_timestamp = int(two_weeks_ago.timestamp() * 1000)
numberOfDays = 12


def init():
    print("Starting handler")
    sales_demo_company = '115936'
    result = get_inspections(sales_demo_company)
    print(result)
    print('got all inspections, about to iterate them, count:' + str(len(result)))
    input()
    iterate_inspections(result, sales_demo_company)
    print("Finished handler")


def iterate_inspections(result, company_id):
    for i in result:
        id_ = i["id"]
        delete_inspection(id_)
    import_inspections(company_id)


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


def get_inspections(company_id):
    start_pos = 0
    response = None
    inspections = []
    # while response is None or (response.json()['inspections'].__len__()) > 0:
    response = requests.get(base_url + f"/api/export?fromPeriod={numberOfDays}d&companyId=" + str(company_id), headers=headers)
    response.raise_for_status()
    # print("response",response.json)
    inspections = inspections + response.json()['inspections']
    # start_pos += 50
    print(response.json()['inspections'].__len__())

    return inspections


def delete_inspection(inspection_id):
    if inspection_id not in DO_NOT_ERASE:
        print("Deleting inspection: " + inspection_id)
        # response = requests.delete(base_url + "/api/delete?inspectionId=" + inspection_id, headers=headers) TODO to be removed!
        # response.raise_for_status()
    else:
        print("We are not erasing ",inspection_id)

## review this function
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
                response = requests.post(base_url + '/api/import?companyId=' + company_id, json=json_data,headers=import_headers)
                response.raise_for_status()
                print(json_file, 'was imported successfully', response.text)

init()