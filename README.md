AuroraChecker is a simple CLI tool that pulls Auora data from NOAA and notifies you when there are changes to your probability of seeing an Aurora in the location you specify. The simplest way to run the command is "python aurorachecker.py [latitude] [longitude]". You can also run "python aurorachecker.py -h" to see a full list of options and additional help:

usage: AuroraChecker [-h] [-gl] [-t THRESHOLD] [-i INTERVAL] [-q] [-g] latitude longitude
Checks NOAA for Aurora predictions and alerts you when the prediction changes

positional arguments:

latitude latitude of the place you want to see the chances of an Aurora. Can be either cardinal (Ex: 58S) or decimal (Ex: -58)

longitude longitude of the place you want to see the chances of an Aurora. Can be either cardinal (Ex: 40W) or decimal (Ex: -40)

options:

-h, --help show this help message and exit

-gl, --notifyglobal set this flag if you want text output when the NOAA forcast has been updated even if your areas chances haven't change

-t THRESHOLD, --threshold THRESHOLD sets the Aurora probabilty threshold where you will recieve text output. The default is 0

-i INTERVAL, --interval INTERVAL set the time in seconds between requests to NOAA for new data. The default is 90 seconds

-q, --quiet set this flag to make it so the only text output you get is updates to your locations probablity

-g, --graph set this flag to display graphs
