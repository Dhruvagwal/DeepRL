import requests
import json
import time
import firebase_admin
from firebase_admin import credentials, db
import random
import math
cred = credentials.Certificate("./fb.json")
default_app = firebase_admin.initialize_app(
    cred, {'databaseURL': 'https://hypervisionp-default-rtdb.firebaseio.com/'})


def getPrediction():
    value1 = random.choice(
        [1, 2, 5, 10, 200, 100, 400, 300])  # spin result
    value2 = random.choice(
        [1, 2, 5, 10, 200, 100, 400, 300])  # slot result

    value3 = random.choice([1, 2, 3, 4, 10, 50])  # slot multiplier

    if value1 != value2:
        if value1 <= 10:  # check if event belongs to 1,2,5,10
            mul = value1
        else:  # if not then just store _ value
            mul = "_"
    else:
        if value1 <= 10:  # check if event belongs to 1,2,5,10
            mul = value1*value3
        else:  # if not then just store _ value
            mul = "_"

    response_dict = {'spin_result': value1, 'result': value2,
                     'slot_multiplier': value3, 'multiplier': mul, "conf": random.randint(0, 100)}
    return response_dict


def updateFB():
    result = getPrediction()
    total_count = 0
    total_pass = 0
    while True:
        response = requests.get('https://api.tracksino.com/crazytime_history',
                                params={
                                    "filter": "",
                                    "sort_by": "",
                                    "sort_desc": False,
                                    "page_num": 1,
                                    "per_page": 1,
                                    "period": "24hours",
                                },
                                headers={'Authorization': 'Bearer 35423482-f852-453c-97a4-4f5763f4796f'})

        # Make a request to the API and get the current data
        current_data = response.json()
        try:
            with open("previous_data.json", "r") as f:
                previous_data = json.load(f)
        except FileNotFoundError:
            previous_data = None
        # try:
        new_data = current_data["data"][0]
        if previous_data is None or previous_data["round_code"] != new_data["round_code"]:
            total_count += 1
            # print(new_data, previous_data)
            ref = db.reference("/prediction")
            new_result = getPrediction()
            ref.set(new_result)
            acc_ref = db.reference("/accuracy")
            acc_ref.set(round(total_pass/total_count*100))
            storage_ref = db.reference("/history")
            if(new_data["result"]==result["spin_result"]):
                total_pass += 1
            storage_ref.push().set({
                "actual": new_data,
                "prediction": result,
            })
            result = new_result
            # Save the current data as the new previous state
            with open("previous_data.json", "w") as f:
                json.dump(current_data["data"][0], f)
        else:
            print("Same")
        # except:
        #     print("Internal Server Error Please Contct to developer dhruvagwal@gmail.com")

        # Wait for 1 minute before checking again
        time.sleep(5)


if __name__ == "__main__":
    updateFB()
