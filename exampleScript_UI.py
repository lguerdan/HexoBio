
__author__ = 'antoine'

from os.path import expanduser
import getpass, sys,HxApi2_0
def main(argv):
    '''
    To tests this script, either run it from here, of call "python exampleScript2.py" from the terminal.

    First, login information is taken as input from the user. This will create a token that is used for logging in to
    the database and accessing data.

    Second, an option is chosen from listing records, showing detailed record information, downloading one or multiple
    records, and quitting.

    Do not forget to enter your developper keys below
    '''

    publicKey = "somelettersandnumbers"
    privateKey = "somemorelettersandnumbers"


    index=0

    while index<10:
        print 'Please enter login information'
        username = raw_input('Username : ')
        password = getpass.getpass('Password : ')
        try:
            #Create login authentication token
            auth = HxApi2_0.SessionInfo(publicKey=publicKey,privateKey=privateKey,username=username,password=password,base_url='api')
            opt=''
            index=10
        except:
            print 'Bad username or password, try again'
            index+=1
        if len(username)==0:
            print 'No userName entered, will quit'
            index=20


    while index<30:
        #Entering the menu
        opt = raw_input('Choose action to perform :\n\t1 - List records\n\t2 - Show record info'
                        '\n\t3 - Download record\n\t4 - Clear cache (next command will take a while, use if program does not download all)\n\t'
                        'q - Quit.\nSelection :')
        if opt=='1':
            #getRecordList list the records list for the given authentication token
            recList = HxApi2_0.getRecordList(auth,limit="20",user='', deviceFilter='')
            stringInfo = ''
            for r in recList:
                stringInfo+='Session '+str(r['id'])+' - '+r['user'].email+'\n'
            print stringInfo+'\n'
        elif opt=='2':
            recordNo = raw_input('Enter record number : ')
            try:
                #getRecordInfo fetches detailed information about a single record
                data= HxApi2_0.getRecordInfo(auth,recordNo)
                for key,val in data.items():
                    print str(key) + ' : ' + str(val)
            except:
                print "Incorrect value entered, retry with something else"
                index+=1
            print ''
        elif opt=='3':
            selection = raw_input('Enter comma-separated list of records to download :\n\t')
            selection = selection.split(',')
            for r in selection:
                try:
                    data = HxApi2_0.getRecordData(auth,recordID=r)
                    HxApi2_0.saveTxt(data,expanduser('~')+'/Downloads/HexoskinData/')
                except:
                    print "Problem loading record (skipped) : " + str(r)
                    index+=1
        elif opt=='4':
            auth.api.clear_resource_cache()
        elif opt=='q' :
            index=30
        else:
            print "Wrong selection"
            index+=1

if __name__ == "__main__":
    main(sys.argv)
