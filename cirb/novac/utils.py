import re, os
import urllib2, socket
from urllib2 import URLError, HTTPError
import urllib
import logging
from cirb.novac import novacMessageFactory as _

from AccessControl import getSecurityManager

__all__=["called_url", "call_put_url", "call_post_url", "get_properties", "get_user"]

def called_url(request_url, request_headers, params='', lang='fr'): # for exemple : content_type = application/xml
    """
    """
    logger = logging.getLogger('cirb.novac.utils.called_url')
    oldtimeout = socket.getdefaulttimeout()
    results = ''
    url = request_url
    if params:
        url = '%s?%s' % (url, params)
    try:
        socket.setdefaulttimeout(7) # let's wait 7 sec        
        request = urllib2.Request(url)
        for header in request_headers:
            try:
                request.add_header(header.keys()[0], header.values()[0])
            except:
                logger.info(_('headers bad formated'))
        request.add_header('HTTP_ACCEPT_LANGUAGE', '%s-be' % lang)
        opener = urllib2.build_opener()
        results = opener.open(request).read()
    except HTTPError, e:
        exception = _('The server couldn\'t fulfill the request. Error code: %s. Url: %s' % (e.code, url))
        logger.error(exception)
        return False
    except URLError, e:
        exception =  _('We failed to reach a server.<br />Reason: %s'% e.reason)
        logger.error(exception)
        return False
    finally:
        socket.setdefaulttimeout(oldtimeout)
    return results  


def call_put_url(request_url, request_headers, data): # request_headers is a dict
    logger = logging.getLogger('cirb.novac.utils.call_put_url')
    oldtimeout = socket.getdefaulttimeout()
    results = ''
    url = request_url
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        socket.setdefaulttimeout(7) # let's wait 7 sec        
        request = urllib2.Request(url, data=data)
        for header in request_headers:
            try:
                request.add_header(header.keys()[0], header.values()[0])
            except:
                logger.error(_('headers bad formated'))
        request.get_method = lambda: 'PUT'
        results = opener.open(request).read()
    except HTTPError, e:
        exception = _('The server couldn\'t fulfill the request. Error code: %s. Url: %s' % (e.code, url))
        logger.error(exception)
        return False
    except URLError, e:
        exception =  _('We failed to reach a server.<br />Reason: %s'% e.reason)
        logger.error(exception)
        return False
    finally:
        socket.setdefaulttimeout(oldtimeout)
        logger.info(url)
    return results

def call_post_url(request_url, request_headers, params=''): # request_headers is a list of dict
    logger = logging.getLogger('cirb.novac.utils.call_post_url')
    oldtimeout = socket.getdefaulttimeout()
    results = ''
    url = request_url
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        socket.setdefaulttimeout(7) # let's wait 7 sec        
        request = urllib2.Request(url)
        if params:
            request.add_data(params)
        for header in request_headers:
            try:
                request.add_header(header.keys()[0], header.values()[0])
            except:
                logger.info(_('headers bad formated'))
        results = opener.open(request).read()
    except HTTPError, e:
        exception = _('The server couldn\'t fulfill the request. Error code: %s. Url: %s' % (e.code, url))
        logger.info(exception)
        return False
    except URLError, e:
        exception =  _('We failed to reach a server.<br />Reason: %s'% e.reason)
        logger.info(exception)
        return False
    finally:
        socket.setdefaulttimeout(oldtimeout)
        logger.info(url)
    return results  

def get_properties(context, prop, prop_name):
        msgid = _(u"not_available")
        not_avaiable = context.translate(msgid)
        try:
            return prop[prop_name]
        except:
            return not_avaiable
        
def get_user(request):
    user={}    
    from zope.annotation.interfaces import IAnnotations
    enn = IAnnotations(request)
    try:
        user['name'] = '%s %s' % (enn['CAS']['firstname'], enn['CAS']['lastname'])
        user['id'] = getSecurityManager().getUser().getId()
    except:
        user['name'] = getSecurityManager().getUser().getUserName()
        user['id'] = getSecurityManager().getUser().getId()
    return user
