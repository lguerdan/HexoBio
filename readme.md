# Hexoskin Python API Client

A Python client for accessing the Hexoskin API.


## HOWTO use HxApi

Application programming interface for Hexoskin
	This API will let you programmatically access data from your hexoskin account. This includes :
		- Downloading records lists, with filtering options
		- Downloading full record data, including raw signal (ECG, respiration, accelerometer)
		- Downloading only partial record data
		- Saving info in different formats (.txt, pickle, matlab)

The source includes an example script allowing you to download record data. Do not forget to enter your own developper key in the appropriate variables or the script will not work

For the API to work, you will need python 2.7 or more. You will also need the following libraries installed : Pickle, pycurl, requests, urllib and numpy
Also, Matlab-related functionalities need the scipy library.

For users recording with a CHA3000/Astroskin, set the MODEL variable to CHA3000 instead of Hexoskin at the top of HxApi2_0

You can also set the output format of the timestamp in a similar manner. Just set the TIMESTAMP variable at the beginning of HxApi2_0, and TIMESTAMP_FORMAT if using String formats.


## Running example
To access the download user interface example, simply run in shell:
 
     $ python exampleScript_UI.py 
