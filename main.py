import math, requests, sys, argparse
from functools import cmp_to_key
from time import sleep
from datetime import datetime

CHECK_INTERVAL = 90

# Stored as [latitude, longitude]
userLocationDeci = [66, 37]
userLocationCardinal = []

argparser = argparse.ArgumentParser(
    prog="AuroraChecker",
    description="Checks NOAA for Aurora predictions and alerts you when the prediction changes"
)

argparser.add_argument("latitude", help="latitude of the place you want to see the chances of an Aurora. Can be either cardinal or decimal")
argparser.add_argument("longitude", help="longitude of the place you want to see the chances of an Aurora. Can be either cardinal or decimal")
argparser.add_argument("-g", "--notifyglobal", action='store_true', help="set this if you want text output when the NOAA forcast has been updated even if your areas chances haven't change")
argparser.add_argument("-t", "--threshold", type=int, help="sets the Aurora probabilty threshold where you will recieve text output")

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

# Positions provided by NOAA are stored [longitude, latitude]
def sortByDistance(pos1, pos2):
    distance1 = math.sqrt(math.pow((pos1[0] - userLocationDeci[1]), 2) + math.pow((pos1[1] - userLocationDeci[0]), 2))
    distance2 = math.sqrt(math.pow((pos2[0] - userLocationDeci[1]), 2) + math.pow((pos2[1] - userLocationDeci[0]), 2))
    return distance1 - distance2

def main():
    args = argparser.parse_args()
    global userLocationDeci, userLocationCardinal
    userLocationDeci = cardinalCoordsToDeci([args.latitude, args.longitude])
    userLocationCardinal = deciCoordsToCardinal(userLocationDeci)
    print(f"{bcolors.UNDERLINE}Location set to {userLocationCardinal[0]} {userLocationCardinal[1]}{bcolors.ENDC}")

    obsvTime = ""
    closestPrediction = ""
    first = True
    queryCount = 0
    while True:
        print(f"Checking NOAA @ ", datetime.now().time())
        auroraRes = requests.get("https://services.swpc.noaa.gov/json/ovation_aurora_latest.json")

        auroraJson = auroraRes.json()
        if obsvTime != auroraJson["Observation Time"] or first:
            if args.notifyglobal:
                print(f"\t{bcolors.BOLD}UPDATED FORCAST{bcolors.ENDC} @", datetime.now().time())
            coordinateData = auroraJson["coordinates"]
            coordinateData = sorted(coordinateData, key=cmp_to_key(sortByDistance))
            auroraOdds = coordinateData[0][2]
            
            if args.threshold and auroraOdds < args.threshold:
                continue

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
        
# coords = [latitude, longitude]
def cardinalCoordsToDeci(coords):
    latitude = coords[0]
    for i in range(len(latitude)):
        if not latitude[i].isdigit():
            match latitude[i]:
                case 'S':
                    latitude = -1 * int(latitude[0:i])
                case 'N':
                    latitude = int(latitude[0:i])
                case default:
                    raise Exception("latitude incorrectly formatted") 
            break
    longitude = coords[1]
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
    if abs(int(latitude)) > 90:
        raise Exception("Latitude out of range (-90 < latitude < 90)")
    if abs(int(longitude)) > 180:
        raise Exception("Longitude out of range (-180 < longitude < 180 )")
    
    return [int(latitude), int(longitude)]

# coords = [latitude, longitude]
# Assumes decimal coords provided are correct
def deciCoordsToCardinal(coords):
    latitude = coords[0]
    if latitude >= 0:
        latitude = str(latitude) + 'N'
    elif latitude < 0:
        latitude = str(-1 * latitude) + 'S'

    longitude = coords[1]
    if longitude >= 0:
        longitude = str(longitude) + 'W'
    elif longitude < 0:
        longitude = str(-1 * longitude) + 'E'

    return [latitude, longitude]
    


if __name__ == "__main__":
    main()