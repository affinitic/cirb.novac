# -*- coding: UTF-8 -*-
import re, os, json
import urllib2, socket
from urllib2 import URLError, HTTPError
import urllib
import logging
from cirb.novac import novacMessageFactory as _

from AccessControl import getSecurityManager

logger = logging.getLogger('cirb.novac.utils')

def called_url(request_url, request_headers, params=''): # for exemple : content_type = application/xml
    """
    """
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

def get_user(request, context=None):
    user={} 
    #fullname = context.portal_membership.getPersonalPortrait(getSecurityManager().getUser().getId()).getProperty('fullname')
    #if fullname:
    #    user['name'] = fullname
    #else:
    user['name'] = getSecurityManager().getUser().getUserName()
    user['id'] = getSecurityManager().getUser().getId()
    if not user.get('id', False):
        return False
    return user



class Dossier(dict):
    def __init__(self, value, field_list, not_available, has_address=False):
        super(Dossier, self).__init__(value)
        self.field_list = field_list
        self.not_available = not_available        
        self.has_address = has_address
        self.update()
        
    def update(self):
        if self.has_address:
            self.update_address()
        self.update_fields_availability()

    def update_address(self):
        address = []
        nf = self.get('numberFrom', '')
        if nf:
            address.append('%s,' % nf)        
        sn = self.get('streetName', '')
        if sn:
            address.append(sn)            
        zc = self.get('zipcode', '')
        if zc:
            address.append(zc)
        zc = self.get('zipCode', '')
        if zc:
            address.append(zc)              
        muni = self.get('municipality', '')
        if muni:
            address.append(muni)            
        if not address:
            self['address'] = self.not_available
        else:
            try:
                self['address'] = u' '.join(address)
            except UnicodeDecodeError, e:
                self['address'] = ' '.join(address)                
                logger.exception(' : %s.' % e.reason)

    def update_fields_availability(self):
        for fieldname in self.field_list:
            self.update_field_availability(fieldname)
            
    def update_field_availability(self, fieldname):
        value = self.get(fieldname, '')
        if not value:
            self[fieldname] = self.not_available


def update_dossiers(dossier_mapping_list, field_list, not_available, has_address=False):
    dossier_list = []    
    for mapping in dossier_mapping_list:
        dossier = Dossier(mapping, field_list, not_available, has_address)
        dossier.update()
        dossier_list.append(dossier)
    return dossier_list
    
    

def json_processing(json_from_ws):
    """
    >>> json_processing({"item":"bier"})
    False
    """
    try:
        jsondata = json.loads(json_from_ws)
    except ValueError, e:
        msg_error = 'Json value error : %s.' % e.message
        logger.error(msg_error)
        return False
    except SyntaxError, e:
        msg_error = 'Json bad formatted : %s.' % e.message
        logger.error(msg_error)
        return False
    return jsondata