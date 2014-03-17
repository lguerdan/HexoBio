__author__ = 'antoine'
"""
synchronous:
    4145 : Acc X,
    4146 : Acc Y,
    4147 : Acc Z
    49 : act1s,
    50 : act15s,
    51 : act5m
    16 : ecg
    19 : hr
    36 : mv (minute ventilation),
    37 : vt (ventilation time)
    33 : respiration rate r_rr
    4129 : resp thoracic, 4130 : resp abdominal
    1000 : HR-quality, 1001, BR-quality, 1002: spo2-quality
    64  :  PPG  PPG_CHANNEL_CHAR
    66  : SPO2  Oxygen saturation.", "freq": 1,
    98  : Blood Pressure
asynchronous:
    34 : respiration inspiration,
    35 : expiration
    247 : Battery level
    52 : step detection count
    18 : qrs interval e_rr
    17 : qrs
    22 : qrs amplitude
    212 : button annotation
    97:  Pulse Transit Time
"""


import os
import base64
import sys

from numpy import fromstring
import hexoskin.client
import hexoskin.errors
import apiErrors

raw_datatypes = {'accx' : 4145,
    'accy' : 4146,
    'accz' : 4147,
    'ecg' : 4113,
    'ecg2' : 4114,
    'ecg3' : 4115,
    'resp_thor' : 4129,
    'resp_abdo' : 4130,
    'temperature' : 81,
    'ppg' : 64
}

datatypes = {'activity' : 49,
    'cadence' : 53,
    'heartrate' : 19,
    'minuteventilation' : 36,
    'vt' : 37,
    'breathingrate' : 33,
    'hr_quality' : 1000,
    'br_quality' : 1001,
    'spo2_quality' : 1002,
    'spo2' : 66,
    'systolicpressure' : 98,
    'inspiration' : 34,
    'expiration' : 35,
    'batt' : 247,
    'step' : 52,
    'rrinterval' : 18,
    # 'qrs_old' : 17, # Removed because datatype 17 has been deprecated
    'qrs' : 22,
    'button_annot' : 212,
    'ptt' : 97,
    'annot':208
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
    raw_dat = {}
    dat = {}
    final_dat = {}
    record = auth.api.record.get(recordID)
    if downloadRaw == True:
        raw_dat = auth.api.data.list(record=recordID,datatype__in=raw_datatypes.values())
        final_dat.update(raw_dat.response.result[0].data.items())
    dat = auth.api.data.list(record=recordID,datatype__in=datatypes.values())
    final_dat.update(dat.response.result[0].data.items())
    for k,v in datatypes.iteritems():
        try:
            final_dat[k] = final_dat.pop(v)
        except:
            print "No datatype found : " + str(v) + "-" + str(k)
    if downloadRaw == True:
        for k,v in raw_datatypes.iteritems():
            try:
                #Replace dict keys from datatype id to datatype name
                final_dat[k] = final_dat.pop(v)
            except:
                print "No datatype found : " + str(v) + "-" + str(k)
    final_dat['annotations'] = getRangeList(auth, limit="50", user=record.user.id , start=record.start, end=record.end)
    final_dat['info'] = record.fields
    final_dat = compressData(final_dat)
    return final_dat

def getRangeData(auth,rangeID, downloadRaw=True):
    raw_dat = {}
    dat = {}
    final_dat = {}
    rng = auth.api.range.get(rangeID)
    user = rng.user.split('/')[-2]
    if downloadRaw == True:
        raw_dat = auth.api.data.list(range=rangeID,datatype__in=raw_datatypes.values())
        final_dat.update(raw_dat.response.result[0].data.items())
    dat = auth.api.data.list(range=rangeID,datatype__in=datatypes.values())

    final_dat.update(dat.response.result[0].data.items())
    for k,v in datatypes.iteritems():
        try:
            final_dat[k] = final_dat.pop(v)
        except:
            print "No datatype found : " + str(v) + "-" + str(k)
    if downloadRaw == True:
        for k,v in raw_datatypes.iteritems():
            try:
                final_dat[k] = final_dat.pop(v)
            except:
                print "No datatype found : " + str(v) + "-" + str(k)
    final_dat['annotations'] = getRangeList(auth, limit="50", user=user , start=rng.start, end=rng.end)
    final_dat['info'] = rng.fields
    final_dat = compressData(final_dat)
    return final_dat

def getRecordList(auth, limit="20", user='', deviceFilter=''):
    """
    Returns the results list corresponding to the selected filters
        @param auth:            The authentication token to use for the call
        @param limit:           The limit of results to return. Passing 0 returns all the records
        @param userFilter:      The ID of the user to look for
        @param deviceFilter:    The device ID to look for. Takes the form HXSKIN12XXXXXXXX, where XXXXXXXX is the
                                0-padded serial number. Example : HXSKIN1200001234
        @return :               The record list
    """
    #TODO : if limit = 0 or 1000+, return correctly
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
    #TODO : if limit = 0 or 1000+, return correctly
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

def clearCache(auth):
    auth.api.clear_resource_cache()

def compressData(data):
    #Very slow, find faster way around.
    for k,v in data.items():
        if v == []:
            data.pop(k)
    if 'accx' in data:
        # If acceleration is present in the data
        data['acceleration'] = zip(*[[x[0] for x in data['accx']],[x[1] for x in data['accx']],[x[1] for x in data['accy']],[x[1] for x in data['accz']]])
        data.pop('accx')
        data.pop('accy')
        data.pop('accz')
    if 'ecg2' in data:
        # If more than one ecg lead is present in the data
        data['ecg'] = zip(*[[x[0] for x in data['ecg']],[x[1] for x in data['ecg']],[x[1] for x in data['ecg2']],[x[1] for x in data['ecg3']]])
        data.pop('ecg2')
        data.pop('ecg3')
    if 'resp_thor' in data:
        data['respiration'] = zip(*[[x[0] for x in data['resp_thor']],[x[1] for x in data['resp_thor']],[x[1] for x in data['resp_abdo']]])
    return data

def saveRecordList(auth, recordList, mode, dirName="", limit='0', downloadRaw=True):
    """
    Save a record list in the selected format. Only the record's information will be saved (no data)
        @param auth :       The authentication token to use for the call
        @param recordList : The record list to save
        @param mode :       The mode under which to save the record list.
        @param downloadRaw :      Downlaod raw signal
        @param dirname :    the directory under which to save the data
    """
    #TODO return error code if not saved correctly?
    """save all records in a recordlist"""
    mode = mode.lower()
    for record in recordList:
        sessId = record['sessionId']
        info1 = getRecordInfo(auth, sessId, limit)

        python = not os.path.isfile(os.path.join(dirName, info1['username'], 'session' + str(info1['sessionId']), 'dataFile.pkl'))
        matlab = not os.path.isfile(os.path.join(dirName, info1['username'], 'session' + str(info1['sessionId']), 'dataFile.mat'))
        if mode == 'python' and python or mode == 'matlab' and matlab or mode == 'pythonnumpymatlab' and (python or matlab):
            data = getRecord(auth, sessId, 0, downloadRaw)
            print "saving session:" + str(sessId)
            if mode == 'python':
                savePython(data, dirName)
            elif mode == 'pythonnumpy':
                savePythonNumpy(data, dirName)
            elif mode == 'matlab':
                saveMatlab(data, dirName)
            elif  mode == 'pythonnumpymatlab':
                saveMatlab(data, dirName)
                savePythonNumpy(data, dirName)
            else:
                raise RuntimeWarning('saving mode not valid')
        else:
            print "data present not saved :" + str(sessId) + ', user:' + info1['username']


def saveTxt(data,dirname):
    # Receive data as a dictionnary. dict key will be the filename, and its values will be contained in the file.
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

def saveMatlab(dataDict, DirName='', fileName=''):
    """Get all data and save it in .mat format
    If data already present in .mat, rewrite"""
    import copy
    import scipy.io
    dataDict = convertToNumpy(dataDict)
    fileName = chooseDir(dataDict, DirName, fileName)
    if  fileName[-3:] == 'mat':
        fileName = fileName[:-4]
    scipy.io.savemat(fileName + '.mat', dataDict, appendmat=True, format='5', long_field_names=False, do_compression=False, oned_as='row')


def convertToNumpy(dataDict):
    import numpy as np
    if 'channels' in dataDict:
        data = dataDict['channels']
        for name1 in data.viewkeys():
            if type(data[name1]) == list:  # this is to access channels
                data2 = np.array(data[name1])
                freq1 = []
                dt = []
                typeSynchro = ['ecg', 'resp', 'acc']
                freqSynchro = [256, 128, 25]
                time1, startTime1, endTime1, data3, freq, dt, annotation = [], [], [], [], [], [], []
                if name1 in typeSynchro:
                    freq1 = freqSynchro[typeSynchro.index(name1)]
                    dt = 256 / freq1
                elif data2.shape[0] > 1:
                    time1 = np.array((data2[:, 0]), dtype=np.int64)
                    time1 = np.array(time1 - time1[0], dtype=np.int32)

                if len(data2.shape) > 1:
                    startTime1 = int(data2[0, 0])
                    endTime1 = int(data2[-1, 0])
                    if data2.shape[1] > 1:
                        if name1 == 'annotation':
                            annotation = list(data2[:, 1:])
                        else:
                            data3 = np.array((data2[:, 1:]), dtype=np.int16)
                dataOut = {'startTime': startTime1,
                           'endTime': endTime1,
                           'freq': freq1,
                           'dt': dt,
                           'time': time1,
                           'data': data3,
                           'annotation': annotation}
                data[name1] = dataOut
    return dataDict

def test_auth(api):
    try:
        api.account.list()
    except hexoskin.errors.HttpUnauthorized, e:
        if e.response.result == '':
            return 'login_invalid'
        elif e.response.result['error'] == 'API signature failed.':
            return 'key_invalid'
    return ''