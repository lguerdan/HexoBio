from os.path import expanduser
import sys, HxApi2_0, os, zipdir, glob, shutil, getopt, traceback
import hexoskin.client
import json as simplejson

def main(argv):

    try:
        args = list(argv)
        username = args[1]
        password = args[2]
        publicKey = args[3]
        privateKey = args[4]

    except Exception, e:
        print str(e)
        print "Useage: <username> <password> <publicKey> <privateKey>"

    auth = HxApi2_0.SessionInfo(publicKey=publicKey,privateKey=privateKey,username=username,password=password)
    records = HxApi2_0.getRecordList(auth, limit = "2000")
    all_recordID = [record['id'] for record in records]

    downloadpath = expanduser('~')+'/Downloads/HexoskinData/'
    recordpath = downloadpath + "records_downloaded.txt"
    files = glob.glob(downloadpath + '/*/*')
    with_inprogress = [int(file.rsplit('_', 1)[1].split('.')[0]) for file in files]

    if set(set(all_recordID) - set(with_inprogress)) == False :
        print "All records up to date."
    else:
        for record in all_recordID[1:len(all_recordID)/2]:
            if record not in with_inprogress:
                try:
                    print 'Downloading record %s'%record
                    data = HxApi2_0.getRecordData(auth,recordID=record)
                    HxApi2_0.saveTxt(data, downloadpath)
                    zipdir.zipdir(glob.glob(downloadpath + '/*/*'+ str(record))[0])
                    shutil.rmtree(glob.glob(downloadpath + '/*/*'+ str(record))[0])
                    with_inprogress.append(record)

                except Exception, e:
                    print str(e)
                    print "Problem loading record : " + str(record)
                    ex_type, ex, tb = sys.exc_info()
                    traceback.print_tb(tb)

    with open(recordpath, 'w') as f:
        f.write(str(len(with_inprogress)) + " records downloaded\n")
        simplejson.dump(with_inprogress.sort(), f)

if __name__ == "__main__":
    main(sys.argv)