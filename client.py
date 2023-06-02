import datetime
import requests
import logging

_LOGGER = logging.getLogger(__name__)


class LoginRequired(Exception):
    def __str__(self):
        return 'Please login first.'
    
class LoginFailed(Exception):
    def __str__(self):
        return 'Login failed, maybe wrong email or password'


class Client(object):
    host = None
    verify = None
    _is_authenticated = None
    _session = None
    token = None
    _email = None
    _passwd = None
    data = None
    expire_time_delta = None
    update_time = None
    
    """class to interact with Nginx Proxy Manager WEB API"""
    def __init__(self, host, verify=True, cache_seconds=30):
        """
        Initialize the client

        :param host: Base URL of the Nginx Proxy Manager WEB API
        :param verify: Boolean to specify if SSL verification should be done.
                       Defaults to True.
        """
        self.host = host.strip('/')
        self.verify = verify
        self._is_authenticated = False
        self.expire_time_delta = datetime.timedelta(seconds=cache_seconds)

    def _get(self, path, params=None, **kwargs):
        """
        Method to perform GET request on the API.

        :param path: path of the API.
        :param kwargs: Other keyword arguments for requests.

        :return: Response of the GET request.
        """
        return self._request(path, 'get', params=params, **kwargs)

    def _post(self, path, json=None, params=None, **kwargs):
        """
        Method to perform POST request on the API.

        :param path: path of the API.
        :param data: POST DATA for the request.
        :param kwargs: Other keyword arguments for requests.

        :return: Response of the POST request.
        """
        return self._request(path, 'post', params=params, json=json, **kwargs)
    
    def _put(self, path, json=None, params=None, **kwargs):
        """
        Method to perform POST request on the API.

        :param path: path of the API.
        :param data: POST DATA for the request.
        :param kwargs: Other keyword arguments for requests.

        :return: Response of the POST request.
        """
        return self._request(path, 'put', params=params, json=json, **kwargs)

    def _request(self, path, method, params=None, json=None, **kwargs):
        """
        Method to hanle both GET and POST requests.

        :param path: path of the API.
        :param method: Method of HTTP request.
        :param data: POST DATA for the request.
        :param kwargs: Other keyword arguments.

        :return: Response for the request.
        """
        final_url = self.host + path

        if not self._is_authenticated:
            raise LoginRequired

        kwargs['verify'] = self.verify
        headers = kwargs.get('headers')
        if not headers:
            headers = {}
        headers['authorization'] = 'Bearer {}'.format(self.token)
        resp = self._session.request(method, final_url, headers=headers, params=params, json=json, **kwargs)
        if resp.status_code == 403 or (type(resp.json()) == dict and resp.json().get('error') and resp.json().get('error', {}).get('code') == 401):
            self.login()
            headers['authorization'] = 'Bearer {}'.format(self.token)
            resp = self._session.request(method, final_url, headers=headers, params=params, json=json, **kwargs)
        return resp

    def login(self, email=None, password=None):
        """
        Method to authenticate the Nginx Proxy Manager Client.

        Declares a class attribute named ``session`` which
        stores the authenticated session if the login is correct.
        Else, shows the login error.

        :param username: Username.
        :param password: Password.

        :return: Response to login request to the API.
        """
        self._session = requests.Session()
        if email:
            self._email = email
        if password:
            self._passwd = password
        
        headers = {
            'authorization': 'Bearer null',
        }

        json_body =  {
            "identity": self._email,
            "secret": self._passwd,
        }  
        path = '/api/tokens'
        
        resp = self._session.post(self.host + path,
                                  headers=headers, 
                                  json=json_body,
                                  verify=self.verify)
        resdata = resp.json() 
        self.token = resdata.get('token')
        if self.token:
            self._is_authenticated = True
        else:
            self._is_authenticated = False
            raise LoginFailed

    def logout(self):
        """
        Logout the current session.
        """
        self.token = None
        self._is_authenticated = False
        
    def _get_proxy_hosts(self):
        args = {
            'expand': 'owner,access_list,certificate',
        }
        return self._get('/api/nginx/proxy-hosts', args).json()

    def _get_access_lists(self):
        args = {
            'expand': 'owner,items,clients',
        }
        return self._get('/api/nginx/access-lists', args).json()
        
    def update_data(self, force=False):
        is_expired = False
        if self.update_time is None:
            is_expired = True
        elif datetime.datetime.now() - self.expire_time_delta > self.update_time:
            is_expired = True
        if is_expired or force:
            _LOGGER.debug('Update data')
            self.update_time = datetime.datetime.now()
            data = {}
            data['proxy_hosts'] = self._get_proxy_hosts()
            data['proxy_hosts_id_map'] =  {v['domain_names'][0]:v['id'] for v in data['proxy_hosts']}
            data['proxy_hosts_access_id_map'] = {v['domain_names'][0]:v['access_list_id'] for v in data['proxy_hosts']}
            data['access_lists'] = self._get_access_lists()
            data['access_map'] = {v['name']:v['id'] for v in data['access_lists']}
            self.data = data
        return self.data

    def put_host_access_id(self, id, access_list_id):
        data = {
            'access_list_id': access_list_id
        }
        return self._put('/api/nginx/proxy-hosts/{}'.format(id), json=data).json()