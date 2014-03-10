import base64, cPickle, hashlib, json, os, re, struct, time, urlparse
import requests
from requests.auth import HTTPBasicAuth
from hexoskin.errors import *


CACHED_API_RESOURCE_LIST = '.api_stash'

class ApiResourceAccessor(object):

    def __init__(self, conf, api):
        self._conf = conf
        self.api = api


    def list(self, get_args=None, **kwargs):
        self._verify_call('list', 'get')
        get_args = get_args or {}
        get_args.update(kwargs)
        get_args = self.api.convert_instances(get_args)
        response = self.api.get(self._conf['list_endpoint'], get_args)

        # TODO: Replace with a reasonable method of determining the response type.
        if type(response.result) is list:
            return ApiDataList(response, self)
        else:
            return ApiResourceList(response, self)


    def patch(self, new_objects, *args, **kwargs):
        self._verify_call('list', 'patch')
        return self.api.patch(self._conf['list_endpoint'], {'objects':new_objects}, *args, **kwargs)


    def get(self, uri):
        self._verify_call('detail', 'get')
        if type(uri) is int or self._conf['list_endpoint'] not in uri:
            uri = '%s%s/' % (self._conf['list_endpoint'], uri)
        response = self.api.get(uri)
        return ApiResourceInstance(response.result, self)


    def create(self, data, *args, **kwargs):
        self._verify_call('list', 'post')
        data = self.api.convert_instances(data)
        response = self.api.post(self._conf['list_endpoint'], data, *args, **kwargs)
        if response.result:
            return ApiResourceInstance(response.result, self)
        else:
            return response.headers['Location']


    def _verify_call(self, access_type, method):
        if method not in self._conf['allowed_%s_http_methods' % access_type]:
            raise MethodNotAllowed('%s method is not allowed on a %s %s' % (method, self._conf['name'], access_type))



class ApiDataList(object):

    def __init__(self, response, parent):
        self._parent = parent
        self.response = response
        for i,v in enumerate(self.response.result):
            self.response.result[i] = ApiDataResult(v, parent)


    def __getitem__(self, key):
        return self.response.result[key]


    def __iter__(self):
        return iter(self.response.result)


    def __reversed__(self):
        return reversed(self.response.result)


    def __len__(self):
        return len(self.response.result)



class ApiDataResult(object):

    def __init__(self, row, parent):
        self.record = [ApiResourceInstance(r, parent.api.record) for r in row.get('record', [])]
        self.data = dict((int(d), v) for d,v in row['data'].items())
        self.user = row['user']



class ApiResourceList(object):

    def __init__(self, response, parent):
        self._parent = parent
        self.response = response
        self.nexturl = None
        self.objects = []
        self._append_response(self.response)


    def next(self):
        if self.nexturl:
            response = self._parent.api.get(self.nexturl)
            self._append_response(response)
        else:
            raise IndexError('List is already at the end.')


    def prev(self):
        if self.prevurl:
            response = self._parent.api.get(self.prevurl)
            self._append_response(response, prepend=True)
        else:
            raise IndexError('List is already at the beginning.')


    def _append_response(self, response, prepend=False):
        self.nexturl = None
        self.prevurl = None
        try:
            self.nexturl = response.result['meta'].get('next', None)
            self.prevurl = response.result['meta'].get('prev', None)
            converted = [ApiResourceInstance(o, self._parent) for o in response.result['objects']]
            if prepend is True:
                self.objects = converted + self.objects
            else:
                self.objects += converted
        except KeyError, e:
            raise ApiError('Cannot parse results, unexpected content received! %s \nFirst 64 chars of content: %s' % (e, response.body[:64]))


    def __getitem__(self, key):
        if type(key) is int:
            return self.objects[key]
        else:
            return self.response.result[key]


    def __delitem__(self, key):
        if type(key) is int:
            self.objects[key].delete()
            del self.objects[key]
        else:
            return super(ApiResourceList, self).__delitem__(key)


    def __iter__(self):
        return iter(self.objects)


    def __reversed__(self):
        return reversed(self.objects)


    def __len__(self):
        return len(self.objects)



class ApiResourceInstance(object):

    def __init__(self, obj, parent):
        # Skip __setattr__ for this one. Should we derive from parent._conf.fields instead?
        self.__dict__['fields'] = obj
        self._parent = parent
        for k,v in self.fields.items():
            if k in parent.api.resource_conf and type(v) is dict and 'resource_uri' in v:
                self.fields[k] = ApiResourceInstance(v, getattr(parent.api, k))


    def __getattr__(self, name):
        if name in self.fields:
            # Special case to decode data fields.
            if name == 'data':
                return self._decode_data()
            return self.fields[name]
        raise AttributeError("Attribute '%s' not found on %s" % (name, self._parent._conf['name']))


    def __setattr__(self, name, value):
        if name in self.__dict__['fields']:
            self.__dict__['fields'].update(self._parent.api.convert_instances({name:value}))
        # elif hasattr(self, name):
        else:
            super(ApiResourceInstance, self).__setattr__(name, value)
        #     raise AttributeError


    def __str__(self):
        return str(self.fields)


    def update(self, data=None, *args, **kwargs):
        self._parent._verify_call('detail', 'put')
        if data is not None:
            for k,v in data.items():
                setattr(self, k, v)
        response = self._parent.api.put(self.fields['resource_uri'], self.fields, *args, **kwargs)

        if response.result:
            self.fields = response.result.copy()


    def delete(self, *args, **kwargs):
        self._parent._verify_call('detail', 'delete')
        response = self._parent.api.delete(self.fields['resource_uri'], *args, **kwargs)
        self.fields = dict((k, None) for k in self.fields.keys())


    def _decode_data(self):
        if not hasattr(self, '_decoded_data'):
            self._decoded_data = None
            for fn in (self._decode_binary, self._decode_array):
                try:
                    self._decoded_data = fn(self.fields['data'])
                    break
                except Exception:
                    pass
        return self._decoded_data


    def _decode_binary(self, data):
        return struct.unpack('i' * self.nsample, base64.b64decode(data))


    def _decode_array(self, data):
        return [tuple(int(i) for i in v.split(',')) for v in data.strip('()[]').split('), (')]


class ApiHelper(object):

    def __init__(self, base_url=None, user_auth=None, api_key=None, api_secret=None, api_version=''):
        super(ApiHelper, self).__init__()
        self.resource_conf = {}
        self.resources = {}
        self._cache = None

        self.base_url = self._parse_base_url(base_url)
        self.auth_user = user_auth
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_version = api_version

        if CACHED_API_RESOURCE_LIST is not None:
            self._cache = ('%s_%s' % (CACHED_API_RESOURCE_LIST, re.sub(r'\W+', '.', '%s:%s' % (self.base_url, self.api_version)))).rstrip('.')


    def __getattr__(self, name):
        if len(self.resources) == 0:
            self.build_resources()
        if name in self.resources:
            return self.resources[name]
        if name in self.resource_conf:
            self.resources[name] = ApiResourceAccessor(self.resource_conf[name], self)
            return self.resources[name]
        else:
            raise AttributeError("'%s' is not a valid API endpoint" % name)


    def clear_resource_cache(self):
        if self._cache is not None:
            if os.path.isfile(self._cache):
                os.remove(self._cache)
                self.resources = {}
                self.resource_conf = {}


    def build_resources(self):
        if self._cache is not None:
            try:
                with open(self._cache, 'r') as f:
                    self.resource_conf = cPickle.load(f)
            except IOError:
                self._fetch_resource_list()
                try:
                    with open(self._cache, 'w+') as f:
                        cPickle.dump(self.resource_conf, f)
                except IOError, e:
                    print "Couldn't write to stash file: %s" % e
        else:
            self._fetch_resource_list()


    def _fetch_resource_list(self):
        resource_list = self.get('/api/v1/').result
        for n,r in resource_list.iteritems():
            self.resource_conf[n] = self.get(r['schema']).result
            self.resource_conf[n]['list_endpoint'] = r['list_endpoint']
            self.resource_conf[n]['name'] = n


    def _parse_base_url(self, base_url):
        parsed = urlparse.urlparse(base_url)
        if parsed.netloc:
            return 'https://' + parsed.netloc
        raise ValueError('Unable to determine URL from provided base_url arg: %s.', base_url)


    def convert_instances(self, value_dict):
        return dict((k,v.resource_uri) if k in self.resources and type(v) is ApiResourceInstance else (k,v) for k,v in value_dict.items())


    def _request(self, path, method, data=None, params=None, auth=None):
        if auth is None:
            auth = self.auth_user
        if data:
            data = json.dumps(data)
        url = self.base_url + path
        headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
        if self.api_version:
            headers['X-HexoAPIVersion'] = self.api_version
        response = ApiResponse(requests.request(method, url, data=data, params=params, headers=headers, auth=HexoAuth(self.api_key, self.api_secret, auth), verify=False), method)
        if response.status_code >= 400:
            self._throw_http_exception(response)
        return response


    def post(self, path, data=None, auth=None):
        return self._request(path, 'post', data, auth=auth)


    def get(self, path, data=None, auth=None):
        return self._request(path, 'get', params=data, auth=auth)


    def put(self, path, data=None, auth=None):
        return self._request(path, 'put', data, auth=auth)


    def patch(self, path, data=None, auth=None):
        return self._request(path, 'patch', data, auth=auth)


    def delete(self, path, auth=None):
        return self._request(path, 'delete', auth=auth)


    def resource_from_uri(self, path):
        if path.startswith(self.base_url):
            path = path[len(self.base_url):]
        uri,id = re.match('^(.+?)(\d+)/$', path).groups()
        for k,r in self.resource_conf.items():
            if r['list_endpoint'] == uri:
                return getattr(self, k).get(id)
        return None


    def _throw_http_exception(self, response):
        if response.status_code == 400:
            raise HttpBadRequest(response)
        if response.status_code == 401:
            raise HttpUnauthorized(response)
        if response.status_code == 403:
            raise HttpForbidden(response)
        if response.status_code == 404:
            raise HttpNotFound(response)
        if response.status_code == 405:
            raise HttpMethodNotAllowed(response)
        if response.status_code == 500:
            raise HttpInternalServerError(response)
        if response.status_code == 501:
            raise HttpNotImplemented(response)
        raise HttpError(response)



class HexoAuth(HTTPBasicAuth):

    def __init__(self, api_key, api_secret, auth_user=None):
        self.username = None
        self.password = None
        self.api_key = api_key
        self.api_secret = api_secret
        if auth_user is not None:
            self.username, self.password = auth_user.split(':')

    def __call__(self, r):
        if self.username and self.password:
            r = super(HexoAuth, self).__call__(r)
        ts = int(time.time())
        digest = hashlib.sha1('%s%s%s' % (self.api_secret, ts, r.url)).hexdigest()
        r.headers['X-HEXOTIMESTAMP'] = ts
        r.headers['X-HEXOAPIKEY'] = self.api_key
        r.headers['X-HEXOAPISIGNATURE'] = digest
        # print '(%s, %s, %s) = %s' % (self.api_secret, ts, r.url, digest)
        return r



class HexoApi(ApiHelper):

    def __init__(self, api_key, api_secret, base_url=None, user_auth=None, api_version=''):
        if base_url is None:
            base_url = 'https://api.hexoskin.com'
        return super(HexoApi, self).__init__(base_url, user_auth, api_key, api_secret, api_version)



class ApiResponse(object):
    """
    This was built before using the excellent `requests` library so now it
    seems a little silly to wrap the requests.response object with a less 
    functional one.  It's here for compatibility now.  TODO: remove.
    """

    def __init__(self, response, method='GET'):
        try:
            self.result = response.json()
        except:
            self.result = response.content
        self.body = response.content
        self.status_code = response.status_code
        self.url = response.request.url
        self.method = method.upper()
        self.response = response

    def success(self):
        200 <= self.status_code < 400

    def __getattr__(self, attr):
        return getattr(self.response, attr)

    def __str__(self):
        return '%s %s %s\n%s' % (self.status_code, self.method.ljust(6), self.url, self.result)

