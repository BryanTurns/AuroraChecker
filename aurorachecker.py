import requests, argparse, time, dateutil.tz
from datetime import datetime


argparser = argparse.ArgumentParser(
    prog="AuroraChecker",
    description="Checks NOAA for Aurora predictions and alerts you when the prediction changes"
)


argparser.add_argument("latitude", help="latitude of the place you want to see the chances of an Aurora. Can be either cardinal (Ex: 58S) or decimal (Ex: -58)")
argparser.add_argument("longitude", help="longitude of the place you want to see the chances of an Aurora. Can be either cardinal (Ex: 40W) or decimal (Ex: -40)")
argparser.add_argument("-g", "--notifyglobal", action='store_true', help="set this flag if you want text output when the NOAA forcast has been updated even if your areas chances haven't change")
argparser.add_argument("-t", "--threshold", type=int, help="sets the Aurora probabilty threshold where you will recieve text output. The default is 0")
argparser.add_argument("-i", "--interval", type=int, help="set the time in seconds between requests to NOAA for new data. The default is 90 seconds")
argparser.add_argument("-q", "--quiet", action='store_true', help="set this flag to make it so the only text output you get is updates to your locations probablity")


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


def main():
    args = argparser.parse_args()
    if args.interval != None:
        CHECK_INTERVAL = args.interval
    else:
        CHECK_INTERVAL = 90
    if args.quiet:
        QUIET = True
    else:
        QUIET = False
    userLocationDeci = cardinalCoordsToDeci([args.latitude, args.longitude])
    userLocationCardinal = deciCoordsToCardinal(userLocationDeci)
    noaaIndex = deciCoordsToNOAAIndicies(userLocationDeci)
    if not args.quiet:
        print(f"{bcolors.UNDERLINE}Location set to {userLocationCardinal[0]} {userLocationCardinal[1]}{bcolors.ENDC}")
    
    prevObsvTime = None
    prevPrediction = None
    while True:
        if not QUIET:
            print(f"Checking NOAA @ {datetime.now().strftime("%H:%M")}")
        try:
            auroraRes = requests.get("https://services.swpc.noaa.gov/json/ovation_aurora_latest.json")
        except Exception as e:
            # Should probably print exception
            print(f"{bcolors.BOLD}No internet/NOAA site down{bcolors.ENDC}")
            exit(1)
        auroraJson = auroraRes.json()
        if prevObsvTime != auroraJson["Observation Time"]:
            if args.notifyglobal and not QUIET:
                print(f"\t{bcolors.BOLD}UPDATED FORCAST{bcolors.ENDC} @", datetime.now().strftime("%H:%M"))
            coordinateData = auroraJson["coordinates"]
            auroraOdds = coordinateData[noaaIndex][2]

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
            if prevPrediction != auroraOdds and (not args.threshold or args.threshold <= auroraOdds) :
                print(f"\t({datetime.now().strftime("%H:%M")}): {bcolors.BOLD}{bcolors.UNDERLINE}UPDATE IN YOUR AREA{bcolors.ENDC}: {oddsString}")
            prevPrediction = auroraOdds

        obsvTime = auroraJson["Observation Time"]
        userTimezone = dateutil.tz.tzoffset("System",  -1 * time.timezone)
        obsvDatetime = datetime.fromisoformat(obsvTime).astimezone(userTimezone)    
        prevObsvTime = obsvTime

        if not QUIET:
            print(f"Last update at {obsvDatetime.time().strftime("%H:%M")}")
        time.sleep(CHECK_INTERVAL)


# coords = [latitude, longitude]
def cardinalCoordsToDeci(coords):
    latitude = coords[0]
    for i in range(len(latitude)):
        if not latitude[i].isdigit():
            match latitude[i].upper():
                case 'S':
                    latitude = -1 * int(latitude[0:i])
                case 'N':
                    latitude = int(latitude[0:i])
                case '-':
                    continue
                case default:
                    raise Exception("latitude incorrectly formatted") 
            break
    longitude = coords[1]
    for i in range(len(longitude)):
        if not longitude[i].isdigit():
            match longitude[i].upper():
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
        print(f"{bcolors.BOLD}Latitude out of range (-90 < latitude < 90){bcolors.ENDC}")
        exit(1)
    if abs(int(longitude)) > 180:
        print(f"{bcolors.BOLD}Longitude out of range (-180 < longitude < 180)")
        exit(1)
    return (int(latitude), int(longitude))


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
    return (latitude, longitude)


def deciCoordsToNOAAIndicies(coords):
    latVal = 90 + coords[0]
    if coords[1] > 0:
        longVal = coords[1]
    else:
        longVal = 180 + (-1 * coords[1])
    index = longVal * 181 + latVal
    return index


if __name__ == "__main__":
    main()