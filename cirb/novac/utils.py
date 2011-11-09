import re, os
import urllib2, socket
from urllib2 import URLError, HTTPError
import urllib

from cirb.novac import novacMessageFactory as _

def called_url(request_url, content_type, params='', lang='fr'): # for exemple : content_type = application/xml
    """
    return from SSO (cas) : 
    {'CONNECTION_TYPE': 'keep-alive', 
    'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1', 
    'HTTP_REFERER': 'http://192.168.103.22:8080/Plone/novac', 
    'SERVER_NAME': 'ubuntu', 
    'GATEWAY_INTERFACE': 'CGI/1.1', 
    'SERVER_SOFTWARE': 'Zope/(2.13.10, python 2.6.7, linux2) ZServer/1.1', 
    'REMOTE_ADDR': '192.168.103.63', 
    'HTTP_ACCEPT_LANGUAGE': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4', 
    'SCRIPT_NAME': '', 
    'REQUEST_METHOD': 'GET', 
    'HTTP_HOST': '192.168.103.22:8080', 
    'PATH_INFO': '/Plone/novac/wawslistprivate_view', 
    'SERVER_PORT': '8080', 
    'SERVER_PROTOCOL': 'HTTP/1.1', 
    'QUERY_STRING': 'ticket=ST-12-UtGcAWe0temAdFpymxaA-cas', 
    'HTTP_ACCEPT_CHARSET': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 
    'channel.creation_time': 1319631740, 
    'HTTP_ACCEPT_ENCODING': 'gzip,deflate,sdch', 
    'HTTP_COOKIE': '_ZopeId="47674318A5H8WR0M3jM"; 
    __ac="Hd3DxhAw9EpdJ44gF5JC6EqNpL7S4KEP02KGBinNgGs0ZWE3ZmEyOUVuY3J5cHQgODQwNzI2MjU3OTch"', 
    'PATH_TRANSLATED': '/Plone/novac/wawslistprivate_view'}
    """
    oldtimeout = socket.getdefaulttimeout()
    results = ''
    url = request_url
    if params:
        url = '%s?%s' % (url, params)
    try:
        socket.setdefaulttimeout(7) # let's wait 7 sec        
        request = urllib2.Request(url)
        request.add_header('Content-Type', content_type)
        request.add_header('ACCEPT', content_type)
        request.add_header('HTTP_ACCEPT_LANGUAGE', '%s-be' % lang)
        opener = urllib2.build_opener()
        results = opener.open(request).read()
    except HTTPError, e:
        return _('The server couldn\'t fulfill the request.<br />Error code: %s' % e.code)
    except URLError, e:
        return _('We failed to reach a server.<br /> Reason: %s'% e.reason)
    finally:
        socket.setdefaulttimeout(oldtimeout)
    return results  


def call_put_url(request_url, content_type, data): # request_headers is a dict
    oldtimeout = socket.getdefaulttimeout()
    results = ''
    url = request_url
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        socket.setdefaulttimeout(7) # let's wait 7 sec        
        request = urllib2.Request(url, data=data)
        request.add_header('Content-Type', content_type)
        request.get_method = lambda: 'PUT'
        results = opener.open(request).read()
    except HTTPError, e:
        return _('The server couldn\'t fulfill the request.<br />Error code: %s' % e.code)
    except URLError, e:
        return _('We failed to reach a server.<br />Reason: %s'% e.reason)
    finally:
        socket.setdefaulttimeout(oldtimeout)
    return results

def call_post_url(request_url, request_headers, params=''): # request_headers is a list of dict
    oldtimeout = socket.getdefaulttimeout()
    results = ''
    url = request_url
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        socket.setdefaulttimeout(7) # let's wait 7 sec        
        request = urllib2.Request(url)
        if params:
            import json
            request.add_data(json.dumps(params))
        for header in request_headers:
            try:
                request.add_header(header.keys()[0], header.values()[0])
            except:
                #TODO LOG
                print 'headers bad formated in call_post_url'
        results = opener.open(request).read()
    except HTTPError, e:
        return _('The server couldn\'t fulfill the request.<br />Error code: %s' % e.code)
    except URLError, e:
        return _('We failed to reach a server.<br />Reason: %s'% e.reason)
    finally:
        socket.setdefaulttimeout(oldtimeout)
    return results  