__author__ = 'antoine'

import sys,HxApi2_0,getpass
from os.path import expanduser

def main(argv):
    '''
    Here is a sample script to get started. Enter your info below, and the recordId you want to download.
    '''

    # Credentials are entered here, directly in the code, and a session authentication token is created
    username = "user@domain.com"
    password = "password"
    publicKey = "somelettersandnumbers"
    privateKey = "somemorelettersandnumbers"
    auth = HxApi2_0.SessionInfo(publicKey=publicKey,privateKey=privateKey,username=username,password=password,base_url='api')
    
    # Enter the ID of the required record in an array, and HxApi.getRecord will try to download the data associated
    # with it. If it manages to do so, HxApi.saveTxt will save it in the desired path with an adequate filename.
    recordId = [12345]
    try:
        for rec in recordId:
            print 'Downloading record %s'%rec
            data = HxApi2_0.getRecordData(auth,recordID=rec)
            HxApi2_0.saveTxt(data,expanduser('~')+'/Downloads/HexoskinData/')
    except:
        print "Problem loading record : " + str(recordId)


if __name__ == "__main__":
    main(sys.argv)
