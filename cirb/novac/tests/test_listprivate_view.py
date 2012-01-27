# -*- coding: UTF-8 -*-
import unittest2 as unittest
class TestListprivateView(unittest.TestCase):
    
    def test_update_dossiers(self):
        from cirb.novac import utils
        table_ids = ["id","refNova","typeDossier","object","streetName",
                         "numberFrom", "numberTo","zipCode", "municipality",
                         "publicInquiry","startPublicInquiry","endPublicInquiry",
                         "statusPermit","codeDossier", "pointCC","dateCC",
                         "languageRequest","dateDossierComplet","specificReference", 
                         "municipalityOwner", "manager"]
        jsondata = [{"id":147987,
                     "languageRequest":"FR", "manager":"",
                     "municipality":"Schaerbeek", "municipalityOwner":"Schaerbeek",
                     "numberFrom":"437", "object":"transformer ou rénover avec modification du volume;",
                     "pointCC":"Non","publicInquiry":"Non","refNova":"PU/207884",
                     "specificReference":"2008/405=179/437","streetName":"Chaussée de Louvain",
                     "typeDossier":"Permis d'urbanisme privé","x":0.0,"y":0.0,"zipcode":"1030"}]
        
        not_available = "not_available"
        results = utils.update_dossiers(jsondata, table_ids, not_available)
        self.assertTrue(isinstance(results, list))
        self.assertTrue(isinstance(results[0], dict))
        self.assertTrue(results[0]['manager'] == not_available)
        
        #test address
        jsondata = [{"municipality":"Schaerbeek"}]
        results = utils.update_dossiers(jsondata, table_ids, not_available, True)
        self.assertFalse(results[0]['address'] == "")
        
