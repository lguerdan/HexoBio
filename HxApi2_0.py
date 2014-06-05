__author__ = 'antoine'
import os
import hexoskin.client
import hexoskin.errors

#Specify Hexoskin or CHA3000
MODEL = 'Hexoskin'

#Datatypes definitions
if MODEL == 'Hexoskin':
    raw_datatypes = {'acc' : [4145,4146,4147],
        'ecg' : [4113],
        'resp' : [4129,4130]}
    datatypes = {'activity' : [49],
        'cadence' : [53],
        'heartrate' : [19],
        'minuteventilation' : [36],
        'vt' : [37],
        'breathingrate' : [33],
        'hr_quality' : [1000],
        'br_quality' : [1001],
        'inspiration' : [34],
        'expiration' : [35],
        'batt' : [247],
        'step' : [52],
        'rrinterval' : [18],
        # 'qrs_old' : 17, # Removed because datatype 17 has been deprecated
        'qrs' : [22],
    #    'button_annot' : [212]
    }
elif MODEL == 'CHA3000':
    raw_datatypes = {'acc' : [4145,4146,4147],
        'ecg' : [4113,4114,4115], # For CHA3000, use 'ecg' : [4113,4114,4115] instead
        'resp' : [4129,4130],
        'temperature' : [81],
        'ppg' : [64] }

    datatypes = {'activity' : [49],
        'cadence' : [53],
        'heartrate' : [19],
        'minuteventilation' : [36],
        'vt' : [37],
        'breathingrate' : [33],
        'hr_quality' : [1000],
        'br_quality' : [1001],
        'spo2_quality' : [1002],
        'spo2' : [66],
        'systolicpressure' : [98],
        'inspiration' : [34],
        'expiration' : [35],
        'batt' : [247],
        'step' : [52],
        'rrinterval' : [18],
        # 'qrs_old' : 17, # Removed because datatype 17 has been deprecated
        'qrs' : [22],
        #'button_annot' : [212],
        'ptt' : [97] }

#Sample rates definitions
dataSampleRate = {
    4145 : 4,
    4146 : 4,
    4147 : 4,
    4113 : 1,
    4114 : 1,
    4115 : 1,
    4129 : 2,
    4130 : 2,
    81 : 256,
    64 : 4,
    49 : 256,
    53 : 256,
    19 : 256,
    36 : 256,
    37 : [],
    33 : 256,
    1000 : 256,
    1001 : 256,
    1002 : 256,
    66 : 256,
    98 : 256,
    34 : 256,
    35 : 256,
    247 : 256,
    52 : [],
    18 : 256,
    22 : 256,
    212 : 256,
    97 : 256,
    208 : 256
}


class SessionInfo:
    """
    This is the class containing your api login information. Instantiate an object of this class and pass it as argument
    to the api calls you make. You can instantiate as many tokens as you want
    """

    def __init__(self, publicKey='null', privateKey='null', username='null', password='null', base_url='api'):
        """
        The init function instantiate your login token. Your API calls will need this to authenticate to our servers
            @param username :   The username to use for creating the token. This will influence what you can and can not
                                see
            @param password :   the password to login in the "username" account
            @param database :   The database to log into. Choices are api for the production database, or sapi for the
                                development database
        """
        if base_url == 'api':
            apiurl = 'https://api.hexoskin.com'
        elif base_url == 'sapi':
            apiurl = 'https://sapi.hexoskin.com'
        elif base_url == 'dapi':
            apiurl = 'https://dapi.hexoskin.com'
        elif base_url == 'lapi':
            apiurl = 'https://lapi.hexoskin.com:4433'
        elif base_url == 'dapi':
            apiurl = 'https://dapi.hexoskin.com'
        else:
            raise NotImplementedError
        print apiurl
        self.api = hexoskin.client.HexoApi(publicKey, privateKey, base_url=apiurl, user_auth=username + ':' + password, api_version='2.0.x')
        authCode = test_auth(self.api)
        if authCode != '':
            raise

def getRecordData(auth,recordID, downloadRaw=True):
    """
    This function allows you to specify a record, and it will manage the download of the different datatypes by itself
    returns a dictionary containing all datatypes in separate entries
    """
    record = auth.api.record.get(recordID)
    final_dat = getData(auth=auth,user=record.user,start=record.start,end=record.end,downloadRaw=downloadRaw)

    final_dat['annotations'] = getRangeList(auth, limit="50", user=record.user.id , start=record.start, end=record.end)
    final_dat['info'] = record.fields
    #final_dat = compressData(final_dat)
    return final_dat

#def getRangeData(auth,rangeID, downloadRaw=True):
#    """
#    Unsupported for now, use getRecordData instead
#    This function allows you to specify a range, and it will manage the download of the different datatypes by itself
#    returns a dictionary containing all datatypes in separate entries
#    """
#    rng = auth.api.range.get(rangeID)
#    final_dat = getData(auth=auth,user=rng.user,start=rng.start,end=rng.end,downloadRaw=downloadRaw)
#
#    final_dat['annotations'] = getRangeList(auth, limit="50", user=rng.user , start=rng.start, end=rng.end)
#    final_dat['info'] = rng.fields
#    #final_dat = compressData(final_dat)
#    return final_dat

def getData(auth,user,start,end,downloadRaw=True):
    """
    This function fetches the specified data range. Called by getRangeData and getRecordData
    """
    final_dat = {}
    if downloadRaw == True:
        for rawID in raw_datatypes:
            print "Downloading" + rawID
            raw_dat = getUnsubsampledData(auth=auth,userID=user,start=start,end=end,dataID=raw_datatypes[rawID])
            final_dat[rawID]=raw_dat
    for dataID in datatypes:
        print "Downloading" + dataID
        data = getUnsubsampledData(auth=auth,userID=user,start=start,end=end,dataID=datatypes[dataID])
        final_dat[dataID]=data
    return final_dat

def getUnsubsampledData(auth,userID,start,end,dataID):
    """
    All data comes in subsampled form if the number of samples exceeds 65535. If this is the case, fetch data
    page by page to prevent getting subsampled data.
    """
    out = []
    datSampRate = dataSampleRate[dataID[0]]   #Number of ticks between each sample
    if datSampRate != []:
        sampPerIter = 65535*datSampRate         #Number of ticks max size not to overflow 65535 max size
        a = start
        b = min(end,a+sampPerIter)
        while a < end:
            dat = auth.api.data.list(start=a,end=b,user=userID,datatype=dataID)
            if len(dat.response.result) > 0:
                ts = zip(*dat.response.result[0][u'data'].values()[0])[0]
                data = [zip(*dat.response.result[0][u'data'][str(v)])[1] for v in dataID]
                out.extend(zip(ts,*data))
            a = min(a + sampPerIter,end)
            b = min(b + sampPerIter,end)
    else:
        dat = auth.api.data.list(start=start,end=end,user=userID,datatype=dataID)
        if dat.response.result != []:
            out.extend(dat.response.result[0]['data'][str(dataID[0])])
    return out


def getRecordList(auth, limit="20", user='', deviceFilter=''):
    """
    Returns the results records corresponding to the selected filters
        @param auth:            The authentication token to use for the call
        @param limit:           The limit of results to return. Passing 0 returns all the records
        @param userFilter:      The ID of the user to look for
        @param deviceFilter:    The device ID to look for. Takes the form HXSKIN12XXXXXXXX, where XXXXXXXX is the
                                0-padded serial number. Example : HXSKIN1200001234
        @return :               The record list
    """
    """Yields all records info"""
    filters = dict()
    if limit != "20":
        filters['limit'] = limit
    if user != '':
        filters['user'] = user
    if deviceFilter != '':
        filters['device'] = deviceFilter
    out = auth.api.record.list(filters)
    return out.response.result['objects']

def getRangeList(auth, limit="20", user='', activitytype='', start='',end=''):
    """
    Returns the results ranges corresponding to the selected filters
    """
    """Yields all records info"""
    filters = dict()
    filters['order_by']='-start'
    if limit != "20":
        filters['limit'] = limit
    if user != '':
        filters['user'] = user
    if activitytype != '':
        filters['activitytype'] = activitytype
    if start != '':
        filters['start__gte'] = start
    if end != '':
        filters['end__lte'] = end
    out = auth.api.range.list(filters)
    return out.response.result['objects']

def getRecordInfo (auth, recordID):
    """
    Get selected record information
        @param auth :       The authentication token to use for the call
        @param recordID :   The record to save's ID
        @return :           A dictionary of record information
    """
    # extract (version hardware, version software, user info, group)
    obj = auth.api.record.get(recordID)
    return obj.fields

def clearCache(auth):
    """
    This function clears the API cache. To be used only if the resource list changes, which shouldn't happen often
    """
    auth.api.clear_resource_cache()

def saveTxt(data,dirname):
    # Receive data as a dictionnary. dict key will be the filename, and its values will be contained in the file.
    dirname = dirname + str(data['info'][u'user'].email) + '/' + str(data['info']['id'])+ '/' #construct a reasonable name for the file
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    for k,v in data.items():
        filestring = ''
        f = open(dirname + str(k) + '.txt', "w")
        if k == 'info':
            for kk, vv in v.items():
                filestring += '%s : %s\n' % (str(kk),str(vv))
            pass
        elif k == 'annotations':
            for e in v:
                filestring += '%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n' % (e['rank'], e['start'], e['end'], e['id'], e['name'], e['trainingroutine'], e['note'] )
        else:
            for entry in v:
                linelen = len(entry)
                for i, entrySub in enumerate(entry):
                    if i == 0:
                        filestring += (str(long(round(entrySub))) + '\t')  # if timestamp is a float, convert to long integer
                    elif i < linelen-1:
                        filestring += (str(entrySub) + '\t')
                    else:
                        filestring += (str(entrySub) + '\n')
        f.write(filestring)
        f.close()

#def saveMatlab(dataDict, dirname):
#    """Get all data and save it in .mat format
#    Unsupported for now. Use saveTxt
#    If data already present in .mat, rewrite"""
#    import scipy.io
#    if not os.path.isdir(dirname):
#        os.makedirs(dirname)
#
#    #Necessary as
#    dataDict.pop('info')
#    dataDict.pop('annotations')
#
#    scipy.io.savemat(dirname + 'data.mat', dataDict, appendmat=True, format='5', long_field_names=False, do_compression=False, oned_as='row')

def test_auth(api):
    try:
        api.account.list()
    except hexoskin.errors.HttpUnauthorized, e:
        if e.response.result == '':
            return 'login_invalid'
        elif e.response.result['error'] == 'API signature failed.':
            return 'key_invalid'
    return ''