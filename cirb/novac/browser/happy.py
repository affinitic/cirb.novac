# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

import logging, os, urllib, urllib2, socket, json
from urllib2 import URLError, HTTPError
from cirb.novac.browser.publicview import PUB_DOSSIER

class Happy(BrowserView):
    """
    happy pag browser view
    """

    def __init__(self, context, request):
	self.context = context
	self.request = request
	self.logger = logging.getLogger('cirb.novac.happy')	
	novac_url = os.environ.get("novac_url", None)
	if novac_url:
	    self.novac_url = novac_url
	else:
	    registry = getUtility(IRegistry)
	    self.novac_url = registry['cirb.novac.novac_url']

    @property
    def portal_catalog(self):
	return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
	return getToolByName(self.context, 'portal_url').getPortalObject()

    def happy(self):
	results=[]
	results.append(self.get_sso())
	results.append(self.get_waws())
	results.append(self.get_urbis())
	results.append(self.access_database())
	results.append(self.plone_version())
	return results

    def get_sso(self):
	url = "https://sso.irisnet.be/"
	results = get_service(url)
	if results.get('status') == 'ko':
	    return  results
	else:
	    return {'status':results.get('status'), 'message':'access to %s.' % url}

    def get_waws(self):
	id_dossier = '200000'
	url = '%s/%s/%s' % (self.novac_url, PUB_DOSSIER, id_dossier)
	results = get_service(url)
	if results.get('status') == 'ko':
	    return  {'status':results.get('status'),  'message':'%s. dossier : %s.' % (results.get("message"), id_dossier)}
	else:
	    return {'status':results.get('status'), 'message':'access to %s.' % url}


    def get_urbis(self):        
	url = "%s/gis/geoserver/nova/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=CLUSTER3KM&outputFormat=json" % self.context.portal_url()
	res_json = get_service(url)
	if res_json.get('status', '') == 'ko':
	    return  {'status':res_json.get('status'),  'message':'Urbis not found. %s.' % (res_json.get("message"))}
	resutls = json_proccessing(res_json.get("message"))
	tot = 0
	for feature in resutls.get('features'):
	    tot += feature.get('properties').get('NBR_DOSSIERS')
	return {"status":"ok", "message": "Number of dossier in Publicis %s." % tot}


    def access_database(self):
	users = ['bsuttor']
	return {"status":"ok", "message":"Access to db, number of users is %s." % len(users)}

    def plone_version(self):
	ver = 'beta'
	return {"status":"ok", "message":"Plone version is %s." % ver}
    
    def disk_usage(self):
	du = 'du'
	return {"status":"ok", "message":"Plone version is %s." % ver}	


def get_service(url, headers="", params=""):
    logger = logging.getLogger('cirb.novac.happy')
    oldtimeout = socket.getdefaulttimeout()
    results = ''
    if params:
	url = '%s?%s' % (url, params)
    try:
	socket.setdefaulttimeout(7) # let's wait 7 sec        
	request = urllib2.Request(url)
	for header in headers:
	    try:
		request.add_header(header.keys()[0], header.values()[0])
	    except:
		logger.info('headers bad formated')
	opener = urllib2.build_opener()
	results = opener.open(request).read()
    except HTTPError, e:
	exception = 'The server couldn\'t fulfill the request. URL : %s ' % url
	logger.error(exception)
	return {"status":'ko', "message": "%s : %s" % (e.code, e.msg)}
    except URLError, e:
	exception =  'We failed to reach a server. URL: %s' % url
	logger.error(exception)
	return {"status":'ko', "message": "%s : %s" % (e.code, e.reason)}

    finally:
	socket.setdefaulttimeout(oldtimeout)
    return {'status':'ok', 'message': results}

def json_proccessing(res_json):
    logger = logging.getLogger('cirb.novac.happy')
    try:
	jsondata = json.loads(res_json)
    except ValueError, e:
	msg_error = 'Json value error : %s.' % e.message
	logger.error(msg_error)
	return {"status":'ko', "message": msg_error}
    except SyntaxError, e:
	msg_error = 'Json bad formatted : %s.' % e.message
	logger.error(msg_error)
	return {"status":'ko', "message": msg_error}
    return jsondata