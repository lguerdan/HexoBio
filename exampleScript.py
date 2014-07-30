__author__ = 'antoine'

from os.path import expanduser
import sys,HxApi2_0

def main(argv):
    '''
    Here is a sample script to get started. Enter your info below, and the recordId you want to download. If you want,
    you can also change the downloadpath. See the readme for more information
    '''

    # Credentials are entered here, directly in the code
    username = "user@domain.com"
    password = "password"
    publicKey = "somelettersandnumbers"
    privateKey = "somemorelettersandnumbers"

    # Enter the ID of the required record in an array, and HxApi2_0.getRecordData will try to download the data associated
    # with it. If it manages to do so, HxApi2_0.saveTxt will save it in the desired path with an adequate filename.
    recordId = [12345]

    # Select download location. expanduser('~')+'/Downloads/HexoskinData/' will download in your user's downloads folder.
    downloadpath = expanduser('~')+'/Downloads/HexoskinData/'

    # Create authentication token, start fetching data and save it on your computer
    auth = HxApi2_0.SessionInfo(publicKey=publicKey,privateKey=privateKey,username=username,password=password)
    try:
        for rec in recordId:
            print 'Downloading record %s'%rec
            data = HxApi2_0.getRecordData(auth,recordID=rec)
            HxApi2_0.saveTxt(data, downloadpath)
    except:
        print "Problem loading record : " + str(recordId)


if __name__ == "__main__":
    main(sys.argv)
