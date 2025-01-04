import json, math, requests
from functools import cmp_to_key
from time import sleep
from datetime import datetime

userLocation = [148, 65]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def sortByDistance(pos1, pos2):
    distance1 = math.sqrt(math.pow((pos1[0] - userLocation[0]), 2) + math.pow((pos1[1] - userLocation[1]), 2))
    distance2 = math.sqrt(math.pow((pos2[0] - userLocation[0]), 2) + math.pow((pos2[1] - userLocation[1]), 2))
    return distance1 - distance2

def main():
    obsvTime = ""
    while True:
        print("Checking NOAA")
        res = requests.get("https://services.swpc.noaa.gov/json/ovation_aurora_latest.json")
        auroraJson = res.json()
        if obsvTime != auroraJson["Observation Time"]:
            print(f"{bcolors.FAIL}UPDATED FORCAST{bcolors.ENDC} @", datetime.now().time())
            coordinateData = auroraJson["coordinates"]
            coordinateData = sorted(coordinateData, key=cmp_to_key(sortByDistance))
            print(coordinateData[0:5])

        obsvTime = auroraJson["Observation Time"]
        

        
        
        sleep(30)
        

if __name__ == "__main__":
    main()