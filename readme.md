# Hexoskin Python API Client
A Python client for accessing the Hexoskin API.


## What can I use HxApi2_0 for?
This API will let you programmatically access data from your hexoskin account. This includes :
    - Downloading records lists, with filtering options
    - Downloading full record data, including raw signal (ECG, respiration, accelerometer)
    - Downloading only partial record data, certain channels only for example
    - Saving info in different formats (Epoch, human-formatted timestamps)


## Use example scripts
For the API to work, you will need python 2.7 or more. You will also need the following libraries installed : Pickle, pycurl, requests and urllib.

The example scripts are designed to require very little setup and show basic API functionality while being very useful. If you wish to access your data easily, then the example scripts are there for you.
Both scripts download Hexoskin data for the specified records and save it in .txt format.

    exampleScript.py is the most basic implementation. Just input your credential at the beginning of the script, along with your developper keys. Then input the desired record id to download, and fire up the script!
    exampleScript_UI.py is a bit more complete and allows you to input your credentials during execution (with the password not shown during input and never stored). Using a very simple text-based interface, it allows you to download your data.


## Change timestamp output formatting
By default, timestamps are in "Hexotimestamp" (see https://api.hexoskin.com/docs/page/overview/ in the Timestamps section). If you prefer, you can modify this to save files with a more human-friendly way to save the timestamp.
To do that, change the TIMESTAMP variable at the beginning of HxApi2_0.py from "Epoch" to "String". If you want, you can customize the way the string is formatted by changing the TIMESTAMP_FORMAT variable. The documentation for how strings are formatted can be found here: https://docs.python.org/2/library/datetime.html.
The default string output format is: '%Y:%m:%d\t%H:%M:%S:%f', which will yield a timestamp of format 2014:07:25    10:56:11:972656. First is the year, then month, then day, followed by a tab and the hour, minute, second, and microseconds. Removing the %f at the end, for example, will remove the microseconds part.


## CHA3000/Astroskin users
For users recording with a CHA3000/Astroskin, set the MODEL variable to "CHA3000" instead of "Hexoskin" at the top of HxApi2_0 to make sure all the data specific to your model is downloaded.


## Running example from shell
To access the download user interface example from the Shell/Command line, simply run:
 
     $ python exampleScript_UI.py
