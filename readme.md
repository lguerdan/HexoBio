# Hexoskin Python API Client
A Python client for accessing the Hexoskin API. Created by Hexoskin developer team, modified for our use-case


## What can I use HxApi2_0 for?
This API will let you programmatically access data from your hexoskin account. This includes :
    - Downloading records lists, with filtering options
    - Downloading full record data, including raw signal (ECG, respiration, accelerometer)
    - Downloading only partial record data, certain channels only for example
    - Saving info in different formats (Epoch, human-formatted timestamps)


## Change timestamp output formatting
By default, timestamps are in "Hexotimestamp" (see https://api.hexoskin.com/docs/page/overview/ in the Timestamps section). If you prefer, you can modify this to save files with a more human-friendly way to save the timestamp.
To do that, change the TIMESTAMP variable at the beginning of HxApi2_0.py from "Epoch" to "String". If you want, you can customize the way the string is formatted by changing the TIMESTAMP_FORMAT variable. The documentation for how strings are formatted can be found here: https://docs.python.org/2/library/datetime.html.
The default string output format is: '%Y:%m:%d\t%H:%M:%S:%f', which will yield a timestamp of format 2014:07:25    10:56:11:972656. First is the year, then month, then day, followed by a tab and the hour, minute, second, and microseconds. Removing the %f at the end, for example, will remove the microseconds part.



## Running example from shell
To access the download user interface example from the Shell/Command line, simply run:
 
     $ python cravingScript.py <username> <password> <>
