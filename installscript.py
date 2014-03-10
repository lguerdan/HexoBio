import os
# This script tries to install the necessary libraries to use the HxApi functionalities.
# If packages are missing, you will be prompted to install them.

# PyCurl
inst_EZ_inst = False
try:
    import pycurl
    import requests
except Exception, e:
    inst_EZ_inst = True
    print("Missing package detected, installing package(s)")

# easy_install, to install only if dependency packages are not yet installed
if inst_EZ_inst:
    try:
        import easy_install
    except Exception, e:
        print("easy_install not installed. Now trying to install it") 
        try:
            os.system("wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - --no-check-certificate | sudo python")
        except Exception, e2:
            print("Problem installing easy_install, error : %s", e2) 

# PyCurl
try:
    import pycurl
except Exception, e: 
    print("Pycurl not installed. Now trying to install it")
    try:
        os.system("sudo easy_install pycurl")
    except Exception, e2:
        print("Problem installing Pycurl, error : %s", e2) 

# requests
try:
    import requests
except Exception, e: 
    print("Requests not installed. Now trying to install it")
    try:
        os.system("sudo easy_install requests")
    except Exception, e2:
        print("Problem installing requests, error : %s", e2)  
