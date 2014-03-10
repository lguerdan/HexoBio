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
raw_datatypes = {'AccX' : 4145,
    'AccY' : 4146,
    'AccZ' : 4147,
    'ecg' : 4113,
    'resp_thoracic' : 4129,
    'resp_abdo' : 4130,
    'ppg' : 64
}

datatypes = {'act1s' : 49,
    'hr' : 19,
    'mv' : 36,
    'vt' : 37,
    'r_rr' : 33,
    'hr_quality' : 1000,
    'br_quality' : 1001,
    'spo2_quality' : 1002,
    'o2_saturation' : 66,
    'blood_pressure' : 98,
    'inspiration' : 34,
    'expiration' : 35,
    'batterylevel' : 247,
    'step_count' : 52,
    'e_rr' : 18,
    'qrs' : 17,
    'qrs_amplitude' : 22,
    'button_annot' : 212,
    'ptt' : 97
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

def getRecordData(auth,recordID, user, downloadRaw=True):
    raw_dat = {}
    dat = {}
    final_dat = {}
    if downloadRaw == True:
        raw_dat = auth.api.datafile.list(record=recordID,datatype__in=raw_datatypes.values())
    dat = auth.api.datafile.list(record=recordID,datatype__in=datatypes.values())
    final_dat.update(raw_dat.response.result[0].data)
    final_dat.update(dat.response.result[0].data)
    return final_dat

def clearCache(auth):
    auth.api.clear_resource_cache()

def test_auth(api):
    try:
        api.account.list()
    except hexoskin.errors.HttpUnauthorized, e:
        if e.response.result == '':
            return 'login_invalid'
        elif e.response.result['error'] == 'API signature failed.':
            return 'key_invalid'
    return ''