# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

import logging, os, urllib, urllib2, socket, json
from urllib2 import URLError, HTTPError
from cirb.novac.browser.publicview import PUB_DOSSIER
from cirb.novac.utils import called_url, json_processing

NUMBER=10
GEOSERVER_STA="http://geoserver.gis.irisnetlab.be"
GEOSERVER_PROD="http://geoserver.gis.irisnet.be"
PUBLIC_IDS="/geoserver/nova/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=nova:NOVA_DOSSIERS&maxFeatures=%s&outputFormat=json" % (str(NUMBER))


class Happy(BrowserView):
    """
    happy page browser view
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
        results.append(self.database_access())
        results.append(self.get_sso())
        results.append(self.get_pub_waws())
        results.append(self.get_urbis())
        results.append(self.disk_usage())
        # TODO return 409 if one ko
        return results

    def get_sso(self):
        url = "https://sso.irisnet.be/"
        results = get_service(url)
        if results.get('status') == 'ko':
            status = results.get('status')
            message = "%s. Calling sso url %s failled" % (results, url)
        else:
            status = results.get('status')
            message = 'Success : access to sso url (%s).' % url
        return {"status":status, "message":message}

    def get_pub_waws(self):
        env = os.environ.get("DEPLOY_ENV", "")
        if env == "production":
            url = GEOSERVER_PROD
        else:
            url = GEOSERVER_STA
        url ="%s%s" % (url, PUBLIC_IDS)
            
        json_from_ws = called_url(url,"")
        if not json_from_ws:
            status = "ko"
            message = "Not able to call GEOSERVER : %s" % url
            return {'status':status, 'message':message}

        dict_ids = json_processing(json_from_ws)
        if not dict_ids: 
            status = "ko"
            message= "Not able to use json from GEOSERVER"
            return {'status':status, 'message':message}

        features = dict_ids.get('features')
        ids = []
        for dossier in features:
            ids.append(dossier.get('id').split('.')[1])
 
        id_dossier = ids[0]

        url = '%s/%s/%s' % (self.novac_url, PUB_DOSSIER, id_dossier)
        results = get_service(url)
        if results.get('status') == 'ko':
            status = results.get('status')
            message = '%s. Access to public dossier %s failled.' % (results.get("message"), id_dossier)
        else:
            status = results.get('status')
            message = 'Access to %s.' % url
        return {'status':status, 'message':message}

    def get_urbis(self):
        url = "%s/gis/geoserver/nova/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=CLUSTER3KM&outputFormat=json" % self.context.portal_url()
        res_json = get_service(url)
        if res_json.get('status', '') == 'ko':
            status = res_json.get('status')
            message = '%s. Urbis not called.' % (res_json.get("message"))
        else:
            resutls = json_proccessing(res_json.get("message"))
            if resutls.get("status") == "ko":
                status = "ko"
                message = "%s. Parsing json failled" % resutls.get("message")
            else:
                tot = 0
                for feature in resutls.get('features'):
                    tot += feature.get('properties').get('NBR_DOSSIERS')
                status = "ok"
                message = "Success : Number of public dossier in Urbis is %s." % tot
        return {"status":status, "message":message}


    def database_access(self):
        membership = getToolByName(self, 'portal_membership')
        try:
            users = membership.listMembers()
            status = "ok"
            message = "Success : access to db, number of users is %s, Plone version is %s" % (len(users),self.plone_version() )
        except:
            status = "ko"
            message = "Access to list members failled, Plone version is %s"	% self.plone_version()    
        return {"status":status, "message":message}

    def plone_version(self):
        migrationTool = getToolByName(self, 'portal_migration')
        return migrationTool.getSoftwareVersion()

    def disk_usage(self):
        s = os.statvfs('/home')
        free = s.f_bsize * s.f_bavail
        free_kb = free/1024
        free_mb = free_kb/1024
        if free_mb < 100:
            status = "Warnings"
            message = "Space left is wake : %s Mb" % free_mb
        elif free_mb < 500 and free_mb >= 100:
            status = "KO"
            message = "No more space on device, avaiability %s Mb." % free_mb
        else:
            status = "ok"
            message = "Partition '/home' avaiability is %s Mb." %free_mb
        return {"status":status, "message":message}

    def get_server_ip(self):
        hn = os.environ.get("HOSTNAME", "")
        ip = socket.gethostbyname(socket.gethostname())
        return "%s" % (hn)



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
