# -*- coding: utf-8 -*-
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting, FunctionalTesting
import cirb.novac

NOVAC = PloneWithPackageLayer(
	    zcml_filename="configure.zcml",
	    zcml_package=cirb.novac,
	    additional_z2_products=(),
	    gs_profile_id='cirb.novac:default',
	    name="NOVAC")

NOVAC_INTEGRATION = IntegrationTesting(
	    bases=(NOVAC,), name="NOVAC_INTEGRATION")


NOVAC_FUNCTIONAL = FunctionalTesting(
	    bases=(NOVAC,), name="NOVAC_FUNCTIONAL")