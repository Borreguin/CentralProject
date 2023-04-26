import requests


url = "http://localhost:9000/api/external/flight-price/_get/process-calendar-information/KBOI/KMAN"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)