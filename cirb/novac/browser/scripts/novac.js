OpenLayers.DOTS_PER_INCH = 90.71428571428572;
OpenLayers.Util.onImageLoadErrorColor = 'transparent';
var map;
var filter_geom , markers_layer, tabberOptions;
var mouseLoc, currentPopup ;
var portal_url;
var gis_url;
var clusters3km;
var current_language;
var dossiers;
var urbislayer, addressResult;

$(window).bind("load", function() {

    $("#accordion").accordion({		
		header : "h3",		
		active : false,		
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
    var clusters1km = new OpenLayers.Layer.WMS(
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
    map.events.register('click', map, executeGetFeatureInfo);


	$("#search_address_button").click(function() {
        searchAddress($('#street').val(),$('#number').val(),$('#post_code').val());
    });

    $("#search_dossiers").click(function() {
        applyDossierFilter();
        
        clusters3km.setVisibility(false);
        clusters1km.setVisibility(false);
        dossiers.maxResolution = 35.0;
        dossiers.redraw();
        
    });


});


function executeGetFeatureInfo(event) {
    mouseLoc = map.getLonLatFromPixel(event.xy);
    //prepare the getFeatureInfo request
    var url = clusters3km.getFullRequestString({
        REQUEST: "GetFeatureInfo",
        BBOX: map.getExtent().toBBOX(),
        X: Math.round(event.xy.x),
        Y: Math.round(event.xy.y),
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
		    result += "'><table width='350' style='table-layout:fixed'><col width='150'><col width='200'><tr><td>Type de permis:</td><td>";
		    result += (getElements(permits[i], "nova", "TYPEDOSSIERFR")[0])?$(getElements(permits[i], "nova", "TYPEDOSSIERFR")[0]).text()+ " ":"";
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

			result+= '">Pour en savoir plus...<a/></td></tr></table></div>';


		}else{

			result += "<div class='tabbertab' title='Vergunning ";
			result += i+1;
			result += "'><table width='350' style='table-layout:fixed'><col width='150'><col width='200'><tr><td>Type vergunning:</td><td>";
			result += (getElements(permits[i], "nova", "TYPEDOSSIERNL")[0])?$(getElements(permits[i], "nova", "TYPEDOSSIERNL")[0]).text()+ " ":"";
			result +="</td><tr></tr><td>Adres :</td><td>";
			result += (getElements(permits[i], "nova", "STREETNAMENL")[0])?$(getElements(permits[i], "nova", "STREETNAMENL")[0]).text()+ " ":"";


			result +=(getElements(permits[i], "nova", "NUMBERPARTFROM")[0])?$(getElements(permits[i], "nova", "NUMBERPARTFROM")[0]).text():"";

			result +=(getElements(permits[i], "nova", "NUMBERPARTTO")[0])? " - "+ $(getElements(permits[i], "nova", "NUMBERPARTTO")[0]).text():"";

			result +="</td></tr><tr><td></td><td>";
			result += (getElements(permits[i], "nova", "ZIPCODE")[0])?$(getElements(permits[i], "nova", "ZIPCODE")[0]).text()+ " ":"" ;

			result += (getElements(permits[i], "nova", "MUNICIPALITYNL")[0])?$(getElements(permits[i], "nova", "MUNICIPALITYNL")[0]).text():"";

			result += "</td></tr><tr><td>Voorwerp van de aanvraag :</td><td>";
			result += (getElements(permits[i], "nova", "OBJECTNL")[0])?$(getElements(permits[i], "nova", "OBJECTNL")[0]).text()+ " ":"";

			result += '</td><tr></tr><tr><td><a target="_blank" href="';
			result += (permits[i].getAttribute("fid"))?absolute_url+"/"+publicurl+"?id=" + permits[i].getAttribute("fid").split('.')[1]:"";

			result += '">Meer informatie...<a/></td></tr></table></div>';
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
}else{
    //Zoom to point
    var zoom = map.getZoom();
    if(zoom >= 4 ){
        if(zoom <= 5){
            map.setCenter(mouseLoc, zoom+1);
        }else{
            map.setCenter(mouseLoc, zoom);
        }
    }else{
        if(zoom > 1){
            map.setCenter(mouseLoc, 4);
        }else{
            map.setCenter(mouseLoc, 2);
        }
    }
}
}



function applyDossierFilter(){
    var cql_filter = "";
    
    //type and status filter
    var type_dossier = "TYPEDOSSIER IS NULL";
    if($('#type_u').is(':checked')) {
    	if(type_dossier != "") type_dossier += " OR ";
    	type_dossier += "TYPEDOSSIER = 'U'";
    }
    if($('#type_l').is(':checked')) {
    	if(type_dossier != "") type_dossier += " OR ";
    	type_dossier += "TYPEDOSSIER = 'L'";
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
    if ($("#commune").val() != 0) cql_filter += "ZIPCODE=" + $("#commune").val();
    if ($("#typedossier").val() != 0) {
        if (cql_filter.length > 1) cql_filter += " AND"; 
        cql_filter += " SUBTYPEDOSSIER=" + $("#typedossier").val();
    }
    if ($("input[name='ep']:checked").val() == "no") {
        if (cql_filter.length > 1) cql_filter += " AND"; 
        cql_filter += " MPP = 'Non'";
    }
    else if ($("input[name='ep']:checked").val() == "yes") {
        if (cql_filter.length > 1) cql_filter += " AND"; 
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
        if (cql_filter.length > 1) cql_filter += " AND";
        cql_filter += " DATECC >= dateParse('dd/MM/yyyy','" + $("#datecc_from").val() + "')";
    }
    if ($("#datecc_to").val() != "") {
        if (cql_filter.length > 1) cql_filter += " AND";
        cql_filter += " DATECC <= dateParse('dd/MM/yyyy','" + $("#datecc_to").val() + "')";
    }
    
    //apply filter
    if (cql_filter != "") {
        dossiers.mergeNewParams({'CQL_FILTER': cql_filter});
    } 

}

function searchAddress(street, number, post_code){

    var parameters = {
	    language: $('#current_language').html(),
        street: street,
		postcode: post_code,
		number: number
    }
    

    var my_url = gis_url+"services/urbis/Rest/Localize/getstreet";
    $.ajax({
        type: "POST",
        url: my_url,
        data: "{'language':'"+$('#current_language').html()+"','address':{'street':{'name':'"+street+"','postcode':'"+post_code+"'},'number':'"+number+"'}}",
        dataType: "text",
        success:  function(json_data) {
            var address_data = $.parseJSON(json_data);
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
            
        },
    });
    

}



