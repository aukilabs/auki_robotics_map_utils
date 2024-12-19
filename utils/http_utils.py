import requests
import logging
import contextlib
from http.client import HTTPConnection

def debug_requests_on():
    '''Switches on logging of the requests module.'''
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def debug_requests_off():
    '''Switches off logging of the requests module, might be some side-effects'''
    HTTPConnection.debuglevel = 0

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.handlers = []
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARNING)
    requests_log.propagate = False

@contextlib.contextmanager
def debug_requests():
    '''Use with 'with'!'''
    debug_requests_on()
    yield
    debug_requests_off()



def send_request(method, url, headers, json_data=None, body=None, timeout=30):
    try:
        response = requests.request(method=method, url=url, headers=headers, data=body,  
                                    json=json_data, timeout=timeout)
        response.raise_for_status()
        return True, response
    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {e}")
        return False, ""


def send_files(method, url, headers, files=None, timeout=30):
    try:
        response = requests.request(method=method, url=url, headers=headers, 
                                    files=files, timeout=timeout)
        response.raise_for_status()
        return True, response
    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {e}")
        return False, ""