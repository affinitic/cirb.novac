# -*- coding: UTF-8 -*-
import unittest2 as unittest
from cirb.novac.browser import publicview
from cirb.novac import utils
from cirb.novac.testing import NOVAC_INTEGRATION
import os

NUMBER=10
GEOSERVER_PROD="http://geoservices-others.irisnet.be"
PUBLIC_IDS="/geoserver/Nova/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=Nova:Dossiers&maxFeatures=%s&outputFormat=json" % (str(NUMBER))

class TestListprivateView(unittest.TestCase):
    layer = NOVAC_INTEGRATION
    ids=[]
    def test_public_ids(self):
        portal = self.layer["portal"]
        url ="%s%s" % (GEOSERVER_PROD, PUBLIC_IDS)

        json_from_ws = utils.called_url(url,"") 
        self.assertNotEqual(json_from_ws, False, "Not able to call GEOSERVER : %s" % url)
      
        dict_ids = utils.json_processing(json_from_ws)
        self.assertNotEqual(dict_ids, False, "Not able to use json from GEOSERVER")

        features = dict_ids.get('features')
        self.assertEqual(len(features), NUMBER)
        
        for dossier in features:
            self.ids.append(dossier.get('id').split('.')[1])
        self.assertEqual(len(self.ids), NUMBER)

        public_view = publicview.PublicView(portal, "")
        url = "%s/%s/%s" % (public_view.novac_url, publicview.PUB_DOSSIER, self.ids[0])

        json_from_ws = public_view.call_ws(url)
        self.assertNotEqual(json_from_ws, False, "Not able to call WAWS : %s" % url)

        dossier = utils.json_processing(json_from_ws)
        self.assertNotEqual(dossier, False, "Not able to use json from WAWS")

        prop_dossier = dossier.get("properties", None)
        self.assertNotEqual(prop_dossier, None)
        
        streetName = prop_dossier.get("streetName", None)
        self.assertNotEqual(streetName, None)
        
        bad_id_dossier = 14
        url = "%s/%s/%s" % (public_view.novac_url, publicview.PUB_DOSSIER, str(bad_id_dossier))
        self.assertFalse(public_view.call_ws(url))

