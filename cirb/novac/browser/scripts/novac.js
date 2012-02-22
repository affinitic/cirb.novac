OpenLayers.DOTS_PER_INCH = 90.71428571428572;
OpenLayers.Util.onImageLoadErrorColor = 'transparent';
var map;
var filter_geom , markers_layer, tabberOptions;
var mouseLoc, currentPopup ;
var portal_url;
var gis_url;
var clusters1km, clusters3km;
var dossiers;
var current_language;
var urbislayer, addressResult;

function executeGetFeatureInfo(event) {
    mouseLoc = map.getLonLatFromPixel(event.xy);
    console.log(mouseLoc);
    var zoom = map.getZoom();
    if (zoom < 3) {
        map.setCenter(mouseLoc, zoom+2);
        return;
    }
    
    //prepare the getFeatureInfo request
    var url = clusters3km.getFullRequestString({
        REQUEST: "GetFeatureInfo",
        BBOX: map.getExtent().toBBOX(),
        X: Math.round(map.events.getMousePosition(event).x),
        Y: Math.round(map.events.getMousePosition(event).y),
        INFO_FORMAT: 'application/vnd.ogc.gml',
        FORMAT: 'application/vnd.ogc.gml',
        LAYERS : "NOVA_DOSSIERS",
        QUERY_LAYERS: "NOVA_DOSSIERS",
        FEATURE_COUNT: 10,
        WIDTH: map.size.w,
        HEIGHT: map.size.h,
        CQL_FILTER: dossiers.params.CQL_FILTER},
        gis_url+"geoserver/wms?");
    //Execute the GetFeatureInfo request and callback the showPointInfo function
    OpenLayers.Request.GET({
        url: url,
        callback: showPointInfo
    });
}

function getElements(obj, ns, tagname) {
    var result = new Array();
    result = obj.getElementsByTagName(ns+":"+tagname)
    if (result.length == 0) result = obj.getElementsByTagName(tagname);
    return result;
}

function showPointInfo(response) {
    console.log("begin showPointInfo");
    //create an xmlDocument based on the getFeatureInfo response
    var xmlDoc;
    if (window.DOMParser)
    {
        parser=new DOMParser();
        xmlDoc=parser.parseFromString(response.responseText,"text/xml");
    }
    else // Internet Explorer
    {
        xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
        xmlDoc.async="false";
        xmlDoc.loadXML(response.responseText);
    } 


    var permits = new Array();
    permits = getElements(xmlDoc, "nova", "NOVA_DOSSIERS");
    var result = "<div id='tabber' class='tabber'>";
    var absolute_url  = $('#absolute_url').html();
	var publicurl = "public"
    //build the result html
    for(i =0; i < permits.length ; i++){
		if(current_language == 'fr'){
		    result += "<div class='tabbertab' title='Permis ";
		    result += i+1;
		    result += "'><table width='350' style='table-layout:fixed'><col width='150'><col width='200'><tr><td>Type de permis :</td><td>";
		    result += (getElements(permits[i], "nova", "TYPEDOSSIERFR")[0])?$(getElements(permits[i], "nova", "TYPEDOSSIERFR")[0]).text().replace("FD","fonctionnaire délégué")+ " ":"";
		    result +="</td><tr></tr><td>Adresse :</td><td>";
		    result += (getElements(permits[i], "nova", "STREETNAMEFR")[0])?$(getElements(permits[i], "nova", "STREETNAMEFR")[0]).text()+ " ":"";

			result +=(getElements(permits[i], "nova", "NUMBERPARTFROM")[0])?$(getElements(permits[i], "nova", "NUMBERPARTFROM")[0]).text():"";

			result +=(getElements(permits[i], "nova", "NUMBERPARTTO")[0])? " - "+ $(getElements(permits[i], "nova", "NUMBERPARTTO")[0]).text():"";

			result +="</td></tr><tr><td></td><td>";
			result += (getElements(permits[i], "nova", "ZIPCODE")[0])?$(getElements(permits[i], "nova", "ZIPCODE")[0]).text()+ " ":"" ;

			result += (getElements(permits[i], "nova", "MUNICIPALITYFR")[0])?$(getElements(permits[i], "nova", "MUNICIPALITYFR")[0]).text():"";

			result += "</td></tr><tr><td>Objet de la demande :</td><td>";
			result += (getElements(permits[i], "nova", "OBJECTFR")[0])?$(getElements(permits[i], "nova", "OBJECTFR")[0]).text()+ " ":"";

			result +='</td><tr></tr><tr><td><a target="_blank" href="';
			result += (permits[i].getAttribute("fid"))?absolute_url+"/"+publicurl+"?id=" + permits[i].getAttribute("fid").split('.')[1]:"";

			result+= '">Pour en savoir plus...</a></td></tr></table></div>';


		}else{

			result += "<div class='tabbertab' title='Vergunning ";
			result += i+1;
			result += "'><table width='350' style='table-layout:fixed'><col width='150'><col width='200'><tr><td>Type vergunning :</td><td>";
			result += (getElements(permits[i], "nova", "TYPEDOSSIERNL")[0])?$(getElements(permits[i], "nova", "TYPEDOSSIERNL")[0]).text()+ " ":"";
			result +="</td><tr></tr><td>Adres :</td><td>";
			result += (getElements(permits[i], "nova", "STREETNAMENL")[0])?$(getElements(permits[i], "nova", "STREETNAMENL")[0]).text()+ " ":"";


			result +=(getElements(permits[i], "nova", "NUMBERPARTFROM")[0])?$(getElements(permits[i], "nova", "NUMBERPARTFROM")[0]).text():"";

			result +=(getElements(permits[i], "nova", "NUMBERPARTTO")[0])? " - "+ $(getElements(permits[i], "nova", "NUMBERPARTTO")[0]).text():"";

			result +="</td></tr><tr><td></td><td>";
			result += (getElements(permits[i], "nova", "ZIPCODE")[0])?$(getElements(permits[i], "nova", "ZIPCODE")[0]).text()+ " ":"" ;

			result += (getElements(permits[i], "nova", "MUNICIPALITYNL")[0])?$(getElements(permits[i], "nova", "MUNICIPALITYNL")[0]).text():"";

			result += "</td></tr><tr><td>Voorwerp van de aanvraag&nbsp;:</td><td>";
			result += (getElements(permits[i], "nova", "OBJECTNL")[0])?$(getElements(permits[i], "nova", "OBJECTNL")[0]).text()+ " ":"";

			result += '</td><tr></tr><tr><td><a target="_blank" href="';
			result += (permits[i].getAttribute("fid"))?absolute_url+"/"+publicurl+"?id=" + permits[i].getAttribute("fid").split('.')[1]:"";

			result += '">Meer informatie...</a></td></tr></table></div>';
		}
	}

    result += "</div>";
    //if there is allready a popup then close it (only 1 popup at a time)
    if(currentPopup){
        currentPopup.hide();
    }
    //if featureInfo is found then show a popup with the information.
    if(result != "<div id='tabber' class='tabber'></div>"){
        currentPopup = new OpenLayers.Popup.FramedCloud("point_info", mouseLoc, new OpenLayers.Size(410,180), result, null, 'true');
        currentPopup.autoSize = false;
            map.addPopup(currentPopup);
        tabberAutomatic(tabberOptions);
        console.log(currentPopup);
    }
    console.log("end showPointInfo");
}

var applyDossierFilter = function(event) {
    var cql_filter = "";
    
    //type and status filter
    var type_dossier = "CATDOSSIER IS NULL";
    if($('#type_u').is(':checked')) {
    	if(type_dossier != "") type_dossier += " OR ";
    	type_dossier += "CATDOSSIER = 'U'";
    }
    if($('#type_l').is(':checked')) {
    	if(type_dossier != "") type_dossier += " OR ";
    	type_dossier += "CATDOSSIER = 'L'";
    }
    if(type_dossier != "") {
        if (cql_filter != "") cql_filter += " AND ";
        cql_filter += "(" + type_dossier + ")";
    }
    var statut_permis = "STATUT_PERMIS_FR IS NULL";
    if($('#canceled').is(':checked')){
    	if(statut_permis != "") statut_permis += " OR ";
        statut_permis += "STATUT_PERMIS_FR = 'Annulé'";
    }
    if($('#refused').is(':checked')){
        if(statut_permis != "") statut_permis += " OR ";
    	statut_permis += "STATUT_PERMIS_FR = 'Refusé'";
    }
    if($('#required').is(':checked')){
        if(statut_permis != "") statut_permis += " OR ";
    	statut_permis += "STATUT_PERMIS_FR = 'Demandé'";
    }
    if($('#granted').is(':checked')){
        if(statut_permis != "") statut_permis += " OR ";
    	statut_permis += "STATUT_PERMIS_FR = 'Octroyé'";
    }
    if(statut_permis != "") {
    	if(cql_filter != "") cql_filter += " AND ";
    	cql_filter += "(" + statut_permis + ")";
    }
    
    //advanced filter
    if ($("#commune").val() != 0) {
        if(cql_filter != "") cql_filter += " AND ";
        cql_filter += "ZIPCODE=" + $("#commune").val();
    }
    if ($("#instance").val() != 0) {
        if(cql_filter != "") cql_filter += " AND ";
        cql_filter += "INSTANCE=" + $("#instance").val();
    }
    if ($("#instance").val() == 2) {
        $("#typedossier").show();
        if ($("#typedossier").val() != 0) {
            if(cql_filter != "") cql_filter += " AND"; 
            cql_filter += " TYPEDOSSIER='" + $("#typedossier").val()+"'";
        }
    }
    else {
        $("#typedossier").hide();
    }
    
    if ($("input[name='ep']:checked").val() == "no") {
        if(cql_filter != "") cql_filter += " AND"; 
        cql_filter += " MPP = 'Non'";
    }
    else if ($("input[name='ep']:checked").val() == "yes") {
        if(cql_filter != "") cql_filter += " AND"; 
        cql_filter += " MPP = 'Oui'";
        var ep_filter = "(";
        $("input[name='ep_status']").each(function(index,element) {
            if ($(element).is(":checked")) {
                if (ep_filter.length > 1) ep_filter += " OR";
                ep_filter += " STATUT_ENQUETE_NL='"+$(element).val()+"'";
            }
        });
        if (ep_filter.length == 1) ep_filter += " STATUT_ENQUETE_NL IS NULL ";
        ep_filter += ")";
        cql_filter += " AND " + ep_filter;
    }
    if ($("#datecc_from").val() != "") {
        $("#datecc_from").removeClass("error");
        if (/^\d{2}[\/-]\d{2}[\/-]\d{4}$/.test($("#datecc_from").val()) == false) {
            $("#datecc_from").addClass("error");
            return;
        }
        if(cql_filter != "") cql_filter += " AND";
        cql_filter += " DATECC >= dateParse('dd/MM/yyyy','" + $("#datecc_from").val() + "')";
    }
    if ($("#datecc_to").val() != "") {
        $("#datecc_to").removeClass("error");
        if (/^\d{2}[\/-]\d{2}[\/-]\d{4}$/.test($("#datecc_to").val()) == false) {
            $("#datecc_to").addClass("error");
            return;
        }
        if(cql_filter != "") cql_filter += " AND";
        cql_filter += " DATECC <= dateParse('dd/MM/yyyy','" + $("#datecc_to").val() + "')";
    }
    
    //apply filter
    if (cql_filter != "") {
        dossiers.mergeNewParams({'CQL_FILTER': cql_filter});
    }
    
    clusters3km.setVisibility(false);
    clusters1km.setVisibility(false);
    dossiers.maxResolution = 35.0;
    dossiers.redraw();
    
    //update export csv visibility
    count_dossiers();
}

function searchAddress(street, number, post_code){

    var parameters = {
	    language: $('#current_language').html(),
        address: street
    }    

    $("#spinner_address").css("visibility","visible");

    var my_url = gis_url+"services/urbis/Rest/Localize/getaddresses";
    $.ajax({
        type: "POST",
        url: my_url,
        data: parameters,
        dataType: "json",
        success:  function(address_data) {
            $("#spinner_address").css("visibility","hidden");
            var x =Number(address_data.result[0].point.x);
            var y =Number(address_data.result[0].point.y);
            if(!(isNaN(x) || isNaN(y)))
            {
                map.setCenter(new OpenLayers.LonLat(x,y), 6);
				addressResult.removeAllFeatures();
				addressResult.addFeatures([new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(x,y))]);
            }
        },
        error:  function(data) {
            $("#spinner_address").css("visibility","hidden");
        }
    });

}


var getDossiersFilter = function () {
    return dossiers.params.CQL_FILTER;
}

// table data
var source =
{
    datatype: "array",
    data: {},
    totalrecords: 1000
};

var count_dossiers = function() {
    var my_url = gis_url+"geoserver/wfs";
    var parameters = {
        service: 'WFS',
        version: '1.1.0',
        request: 'GetFeature',
        typeName: 'NOVA_DOSSIERS',
        cql_filter: getDossiersFilter(),
        resultType: 'hits'
    }
    $.ajax({
        type: "GET",
        url: my_url,
        data: parameters,
        dataType: "xml",
        success:  function(data) {
            totalrecords = $(data.firstChild).attr("numberOfFeatures");
            if (totalrecords < 1000) $("#export_csv").show();
            else $("#export_csv").hide();
        }
    });
}

var get_dossiers_csv = function() {
    var my_url = gis_url+"geoserver/wfs?";
    var fields = 'NO_DOSSIER,RUE,NUMERO_DE,NUMERO_A,CODE_POSTAL,COMMUNE,TYPE_DOSSIER,STATUT,OBJET,DATE_DEBUT_ENQ_PUBLIQUE,DATE_FIN_ENQ_PUBLIQUE,DATE_COMMISSION_CONCERTATION';
    typename = 'NOVA_DOSSIERS_FR';
    console.log(current_language);
    if(current_language == 'nl'){
        fields = 'DOSSIERNUMMER,STRAAT,NUMMER_VAN,NUMMER_TOT,POSTCODE,GEMEENTE,DOSSIERTYPE,STATUUT,VOORWERP,BEGINDATUM_OPENBAAR_ONDERZOEK,ENDDATUM_OPENBAAR_ONDERZOEK,DATUM_OVERLEGCOMMISSIE';
        typename = 'NOVA_DOSSIERS_NL';
    }
    var parameters = {
        service: 'WFS',
        version: '1.1.0',
        request: 'GetFeature',
        typeName: typename,
        cql_filter: getDossiersFilter(),
        outputFormat: 'csv',
        propertyName: fields
    }

    window.location = my_url + $.param(parameters);
}


$(window).bind("load", function() {

    $("#accordion").accordion({		
		header : "h3",		
		active : 2,		
		collapsible : true,		
		autoHeight : false		
	});
	$("#accordion2").accordion({ 
		header      : "h4",
		active      : false,
		collapsible : true,
		autoHeight  : false
	});
	$("input[name='ep'][value='yes']").click(function() { 
        $("#ep_status_div").slideDown();
    });
    $("input[name='ep'][value!='yes']").click(function() { 
        $("#ep_status_div").slideUp();
    });
    

    portal_url = $('#portal_url').html();
    gis_url = portal_url + "/gis/";
    var url_ws_waws = $('#ws_waws').html();
    var json_file  = $('#json_file').html();
    OpenLayers.ImgPath = portal_url+"/++resource++cirb.novac.images/";
    current_language = $('#current_language').html();

    var mapOptions = { 
        resolutions: [34.76915808105469, 17.384579040527345, 8.692289520263673, 4.346144760131836, 2.173072380065918, 1.086536190032959, 0.5432680950164795, 0.2716340475082398, 0.1358170237541199],
        projection: new OpenLayers.Projection('EPSG:31370'),
        maxExtent: new OpenLayers.Bounds(16478.795,19244.928,301307.738,304073.87100000004),
        units: "meters", 
        controls: [new OpenLayers.Control.Navigation(),new OpenLayers.Control.PanZoomBar()],
        theme: portal_url + "/++resource++cirb.novac.scripts/openlayers.css"
    };
    map = new OpenLayers.Map('map', mapOptions );

    //set the baselayer based on the language
    if(current_language == 'fr'){
        urbislayer = new OpenLayers.Layer.WMS(
            "urbisFR",
            gis_url+"geoserver/gwc/service/wms",
            {layers: 'urbisFR', format: 'image/png' },
            { tileSize: new OpenLayers.Size(256,256) }
        );
        map.addLayer(urbislayer);
    }else{
        urbislayer = new OpenLayers.Layer.WMS(
            "urbisNL", 
            gis_url+"geoserver/gwc/service/wms",
            {layers: 'urbisNL', format: 'image/png' },
            { tileSize: new OpenLayers.Size(256,256) }
        );
        map.addLayer(urbislayer);
    }
    
    //municipalities layer
    var municipalities = new OpenLayers.Layer.WMS(
        "Municipalities", 
        gis_url+"geoserver/wms",
        {layers: 'urbis:URB_A_MU ', styles: 'nova_municipalities', transparent: 'true'},
        {singleTile: true, ratio: 1.25, isBaseLayer: false});
    map.addLayer(municipalities);

    //create the highest cluster layer
	clusters3km = new OpenLayers.Layer.WMS(
		"Clusters3km", 
		gis_url+"geoserver/wms",
		{layers: 'nova:CLUSTER3KM', transparent: 'true'},
		{singleTile: true, ratio: 1.25, isBaseLayer: false});
    map.addLayer(clusters3km);

    //create the lowest cluset layer
    clusters1km = new OpenLayers.Layer.WMS(
        "Clusters1km", 
        gis_url+"geoserver/wms",
        {layers: 'nova:CLUSTER1KM', transparent: 'true'},
        {singleTile: true, ratio: 1.25, isBaseLayer: false});
    map.addLayer(clusters1km);


	//create the dossiers layer
	dossiers = new OpenLayers.Layer.WMS(
	    (current_language == 'nl')?"Bouwaanvragen":"Permis d'urbanisme",
		gis_url+"geoserver/wms", 
		{layers: 'nova:NOVA_DOSSIERS', styles:(current_language == 'nl')?"nova_dossiers_nl":"nova_dossiers_fr",transparent: true},
		{singleTile: true, ratio: 1.25, isBaseLayer: false, maxResolution: 7.0});
 	map.addLayer(dossiers);

	
	//add vector layer for the address point
	var defaultStyle = new OpenLayers.Style({
		'pointRadius': 20,
	  	'fillColor': '#BBBBFF',

	  	'fillOpacity': 0.3,
	  	'strokeColor': '#444444'
	});
	var styleMap = new OpenLayers.StyleMap({'default': defaultStyle});
	addressResult = new OpenLayers.Layer.Vector("Address",{styleMap: styleMap});
	map.addLayer(addressResult);


    //add overview map
	var mapOptions2 = {
		    resolutions: [142.857],
		    projection: new OpenLayers.Projection('EPSG:31370'),
		    maxExtent: new OpenLayers.Bounds(140000,153000,160000,173000),
		    units: "meters", 
		    theme: portal_url + "/++resource++cirb.novac.scripts/openlayers.css"
		    };
	//var jplOverview = urbislayer.clone();
	var jplOverview = new OpenLayers.Layer.WMS(
        "Municipalities", 
        gis_url+"geoserver/wms",
        {layers: 'urbis:URB_A_MU ', transparent: 'true'},
        {singleTile: true, ratio: 1, isBaseLayer: true});
	var controlOptions = {
		        maximized: true,
				size : new OpenLayers.Size(140,140),
		        mapOptions: mapOptions2,
		        layers: [jplOverview],
		        maximized: false,
		        autoPan: false
     };
    var overview = new OpenLayers.Control.OverviewMap(controlOptions);
    map.addControl(overview);

    map.setCenter(new OpenLayers.LonLat(150000.0, 170000.0));
    
    //map.events.register('click', map, executeGetFeatureInfo);
    OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {                
        defaultHandlerOptions: {
            'single': true,
            'double': false,
            'pixelTolerance': 0,
            'stopSingle': false,
            'stopDouble': false
        },

        initialize: function(options) {
            this.handlerOptions = OpenLayers.Util.extend(
                {}, this.defaultHandlerOptions
            );
            OpenLayers.Control.prototype.initialize.apply(
                this, arguments
            ); 
            this.handler = new OpenLayers.Handler.Click(
                this, {
                    'click': this.trigger
                }, this.handlerOptions
            );
        }, 

        trigger: function(e) {
            executeGetFeatureInfo(e);
        }

    });
    
    var mapclick = new OpenLayers.Control.Click();
    map.addControl(mapclick);
    mapclick.activate();


	$("#search_address_button").click(function() {
        searchAddress($('#street').val(),$('#number').val(),$('#post_code').val());
    });

    $(".filter input[type='radio'], .filter input[type='checkbox']").bind("click", applyDossierFilter);
    $(".filter select, .filter input[type='text']").bind("change", applyDossierFilter);

    $("#reset_filter").click(function() {
        
        $(".filter input[type='radio'], .filter input[type='checkbox']").unbind("click", applyDossierFilter);
        $(".filter select, .filter input[type='text']").unbind("change", applyDossierFilter);
        
        $(".filter input[type='checkbox']").attr('checked', true);
        $("#commune").val(0);
        $("#typedossier").val(0);
        $("input[name='ep'][value='all']").attr('checked', true);
        $("#ep_status_div").slideUp();
        $("#datecc_from").val("");
        $("#datecc_to").val("");
        
        dossiers.setVisibility(false);
        dossiers.maxResolution = 7.0;
        dossiers.mergeNewParams({'CQL_FILTER': null});
        dossiers.setVisibility(true);
        
        clusters3km.setVisibility(true);
        clusters1km.setVisibility(true);
        
        $(".filter input[type='radio'], .filter input[type='checkbox']").bind("click", applyDossierFilter);
        $(".filter select, .filter input[type='text']").bind("change", applyDossierFilter);
        
        addressResult.removeAllFeatures();
        
    });    

    
    $("#export_csv_button").click(function() {
        get_dossiers_csv();
    });
    
});


