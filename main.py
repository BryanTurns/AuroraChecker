import json, math, requests, sys
from functools import cmp_to_key
from time import sleep
from datetime import datetime

CHECK_INTERVAL = 90

userLocation = [37, 66]

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
    try:
        if len(sys.argv) == 3:
            lattitude = sys.argv[1]
            for i in range(len(lattitude)):
                if not lattitude[i].isdigit():
                    match lattitude[i]:
                        case 'S':
                            lattitude = -1 * int(lattitude[0:i])
                        case 'N':
                            lattitude = int(lattitude[0:i])
                        case default:
                            raise Exception("Lattitude incorrectly formatted") 
                    break
            longitude = sys.argv[2]
            for i in range(len(longitude)):
                if not longitude[i].isdigit():
                    match longitude[i]:
                        case 'W':
                            longitude = -1 * int(longitude[0:i])
                        case 'E':
                            longitude = int(longitude[0:i])
                        case '-':
                              continue
                        case default:
                            raise Exception("Longitude incorrectly formatted") 
                    break
            if abs(int(lattitude)) > 90:
                        raise Exception("Latitude out of range (-90 < latitude < 90)")
            if abs(int(longitude)) > 180:
                        raise Exception("Longitude out of range (-180 < longitude < 180 )")
            global userLocation 
            userLocation = [int(longitude), int(lattitude)]
    except Exception as e:
        print("Invalid command format\nUsage:\nDefault Location (Kulusuk, Alaska): py main.py\nCustom Location: py main.py [Lattitude] [Longitude]")
        print("Error: ", e)
        return
    print(f"Location set to latt {userLocation[0], userLocation[1]}")

    obsvTime = ""
    closestPrediction = ""
    first = True
    queryCount = 0
    while True:
        print(f"Checking NOAA @ ", datetime.now().time())
        auroraRes = requests.get("https://services.swpc.noaa.gov/json/ovation_aurora_latest.json")

        auroraJson = auroraRes.json()
        if obsvTime != auroraJson["Observation Time"] or first:
            print(f"\t{bcolors.BOLD}UPDATED FORCAST{bcolors.ENDC} @", datetime.now().time())
            coordinateData = auroraJson["coordinates"]
            coordinateData = sorted(coordinateData, key=cmp_to_key(sortByDistance))
            auroraOdds = coordinateData[0][2]
            oddsString = bcolors.BOLD
            if auroraOdds >= 70:
                oddsString += f"{bcolors.OKGREEN}{auroraOdds}%{bcolors.ENDC}"
            elif auroraOdds >= 50:
                oddsString += f"{bcolors.OKBLUE}{auroraOdds}%{bcolors.ENDC}"
            elif auroraOdds >= 30: 
                oddsString += f"{bcolors.OKCYAN}{auroraOdds}%{bcolors.ENDC}"
            elif auroraOdds >= 10:
                oddsString += f"{bcolors.WARNING}{auroraOdds}%{bcolors.ENDC}"
            else:
                oddsString += f"{bcolors.FAIL}{auroraOdds}%{bcolors.ENDC}"

            if closestPrediction != coordinateData[0]:
                print(f"\t{bcolors.BOLD}{bcolors.UNDERLINE}UPDATE IN YOUR AREA{bcolors.ENDC}: {oddsString}")
            closestPrediction = coordinateData[0]

            
        obsvTime = auroraJson["Observation Time"]
        # if datetime.now().minute == 0 or first:
        #     kpRes = requests.get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json")
        #     auroraRes = kpRes.json
        

        if first:
            first = False
    
        sleep(CHECK_INTERVAL)
        

if __name__ == "__main__":
    main()