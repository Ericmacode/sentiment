import requests
import time
import json

url = "https://twitter-api-v1-1-enterprise.p.rapidapi.com/base/apitools/followersList"

headers = {
	"X-RapidAPI-Key": "XXXXXXXXXXXXXXXXXXXX",
	"X-RapidAPI-Host": "twitter-api-v1-1-enterprise.p.rapidapi.com"
}

def process_json_file(file_name):
    with open(file_name, 'r') as file:
        
        data = json.load(file)
        users = data['data']['users']
        screen_name = [user['screen_name'] for user in users]
        for index, screen_name in enumerate(screen_name, start=1):
            print(f"{screen_name}")


next_cursor = -1 


while next_cursor != 0:
    querystring = {"apiKey":"XXXXXXXXXXXXXXXXXXXX","resFormat":"json","userId":"1765334861920026625","cursor":next_cursor,"screenName":"ebixyzdex"}
  
    response = requests.get(url, headers=headers, params=querystring)
 
    if response.status_code == 200:
        response_data = response.json()
        next_cursor = response_data.get("data", {}).get("next_cursor")
        with open('result.json', 'w') as file:
            json.dump(response_data, file, indent=4)  
        process_json_file('result.json')

        if next_cursor == 0:
            print("End of list.")
            break
    else:
        print("Error happened while processing request!")
        print(response.json())
        break
    
    time.sleep(5) 

print("End.")