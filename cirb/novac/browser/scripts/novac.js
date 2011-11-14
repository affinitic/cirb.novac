OpenLayers.DOTS_PER_INCH = 90.71428571428572;
OpenLayers.Util.onImageLoadErrorColor = 'transparent';
var map;
var filter_geom , markers_layer, tabberOptions;
var mouseLoc, currentPopup ;
var portal_url;
var clusters3km;
var current_language;
var dossiers;
var urbislayer;
$(document).ready(function() {

    $("#accordion").accordion({active: 2});

    var url_ws_urbis = $('#ws_urbis').html();
    var url_ws_urbis_cache = $('#urbis_cache_url').html();
    var url_ws_waws = $('#ws_waws').html();
    var json_file  = $('#json_file').html();
    portal_url = $('#portal_url').html();
    OpenLayers.ImgPath = portal_url+"/++resource++cirb.novac.images/";
    current_language = $('#current_language').html();
    url = portal_url+"/wfs_request?url="+url_ws_urbis+"&headers=";

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
            "urbisFR",url_ws_urbis_cache,
            {layers: 'urbisFR', format: 'image/png' },
            { tileSize: new OpenLayers.Size(256,256) }
        );
        map.addLayer(urbislayer);
    }else{
    urbislayer = new OpenLayers.Layer.WMS(
        "urbisNL",url_ws_urbis_cache,
        {layers: 'urbisNL', format: 'image/png' },
        { tileSize: new OpenLayers.Size(256,256) }
    );
    map.addLayer(urbislayer);
    }

    //create the highest cluster layer
	clusters3km = new OpenLayers.Layer.WMS(
		"Clusters3km", 
		url_ws_urbis,
		{layers: 'nova:CLUSTER3KM', transparent: 'true',minScale: 50000},
		{singleTile: true, ratio: 1, isBaseLayer: true});
    map.addLayer(clusters3km);

    //create the lowest cluset layer
    var clusters1km = new OpenLayers.Layer.WMS("Clusters1km", url_ws_urbis,{layers: 'nova:CLUSTER1KM', transparent: 'true',minScale: 25000,maxScale:50000});
    map.addLayer(clusters1km);


	//create the dossiers layer
	dossiers = new OpenLayers.Layer.WMS((current_language == 'fr')?"Permis d'urbanisme":"Bouwaanvragen",
			url_ws_urbis, 
			{layers: 'nova:NOVA_DOSSIERS', transparent: true, maxScale: 25000, singleTile: true}
			);
 	map.addLayer(dossiers);

	var mapOptions2 = {
		    resolutions: [139.76915808105469],
		    projection: new OpenLayers.Projection('EPSG:31370'),
		    maxExtent: new OpenLayers.Bounds(140000,150000,160000,177000),
		    units: "meters", 
		    theme: portal_url + "/++resource++cirb.novac.scripts/openlayers.css"
		    };
	var jplOverview = urbislayer.clone();
	var controlOptions = {
		        maximized: true,
				size : new OpenLayers.Size(140,120),
		        mapOptions: mapOptions2,
		        layers: [jplOverview],
     };


    var overview = new OpenLayers.Control.OverviewMap(controlOptions);
    map.addControl(overview);

    map.setCenter(new OpenLayers.LonLat(150000.0, 170000.0));
    map.events.register('click', map, executeGetFeatureInfo);


    $("#search_address_button").click(function() {
        searchAddress($('#street').val(),$('#number').val(),$('#post_code').val());
    });

});


function executeGetFeatureInfo(event) {
    mouseLoc = map.getLonLatFromPixel(event.xy);
    //prepare the getFeatureInfo request
    var url = clusters3km.getFullRequestString({
        REQUEST: "GetFeatureInfo",
        BBOX: map.getExtent().toBBOX(),
        X: event.xy.x,
        Y: event.xy.y,
        INFO_FORMAT: 'application/vnd.ogc.gml',
        FORMAT: 'application/vnd.ogc.gml',
        LAYERS : "NOVA_DOSSIERS",
        QUERY_LAYERS: "NOVA_DOSSIERS",
        FEATURE_COUNT: 10,
        WIDTH: map.size.w,
        HEIGHT: map.size.h},
        portal_url+"/wfs_request?url=http://geoserver.gis.irisnetlab.be/geoserver/wms?");
    //Execute the GetFeatureInfo request and callback the showPointInfo function
    OpenLayers.Request.GET({
        url: url,
        callback: showPointInfo
    });
}

function getElements(obj, ns, tagname) {
    var result = new Array();
    result = obj.getElementsByTagName(tagname);
    if (result.length == 0) result = obj.getElementsByTagName(ns+":"+tagname);
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
    //build the result html
    for(i =0; i < permits.length ; i++){

    if(current_language == 'fr'){
        result += "<div class='tabbertab' title='Permis ";
        result += i+1;
        result += "'><table width='350' style='table-layout:fixed'><col width='150'><col width='200'><tr><td>Type de permis</td><td>";
        result += (getElements(permits[i], "nova", "TYPEDOSSIERFR")[0])?getElements(permits[i], "nova", "TYPEDOSSIERFR")[0].textContent+ " ":"";
        result +="</td><tr></tr><td>Adresse :</td><td>";
        result += (getElements(permits[i], "nova", "STREETNAMEFR")[0])?getElements(permits[i], "nova", "STREETNAMEFR")[0].textContent+ " ":"";

    result +=(getElements(permits[i], "nova", "NUMBERPARTFROM")[0])?getElements(permits[i], "nova", "NUMBERPARTFROM")[0].textContent:"";

    result +=(getElements(permits[i], "nova", "NUMBERPARTTO")[0])? " - "+ getElements(permits[i], "nova", "NUMBERPARTTO")[0].textContent:"";

    result +="</td></tr><tr><td></td><td>";
    result += (getElements(permits[i], "nova", "ZIPCODE")[0])?getElements(permits[i], "nova", "ZIPCODE")[0].textContent+ " ":"" ;

    result += (getElements(permits[i], "nova", "MUNICIPALITYFR")[0])?getElements(permits[i], "nova", "MUNICIPALITYFR")[0].textContent:"";

    result += "</td></tr><tr><td>Objet de la demande :</td><td>";
    result += (getElements(permits[i], "nova", "OBJECTFR")[0])?getElements(permits[i], "nova", "OBJECTFR")[0].textContent+ " ":"";

    result +='</td><tr></tr><tr><td><a href="';
    result += (getElements(permits[i], "nova", "S_IDADDRESS")[0])?absolute_url+"/wawspublic_view?id=" + getElements(permits[i], "nova", "S_IDADDRESS")[0].textContent:"";

    result+= '">Pour en savoir plus...<a/></td></tr></table></div>';


    }else{

    result += "<div class='tabbertab' title='Vergunning ";
    result += i+1;
    result += "'><table width='350' style='table-layout:fixed'><col width='150'><col width='200'><tr><td>Vergunningstype</td><td>";
    result += (getElements(permits[i], "nova", "TYPEDOSSIERNL")[0])?getElements(permits[i], "nova", "TYPEDOSSIERNL")[0].textContent+ " ":"";
    result +="</td><tr></tr><td>Adres :</td><td>";
    result += (getElements(permits[i], "nova", "STREETNAMENL")[0])?getElements(permits[i], "nova", "STREETNAMENL")[0].textContent+ " ":"";

    result +=(getElements(permits[i], "nova", "NUMBERPARTFROM")[0])?getElements(permits[i], "nova", "NUMBERPARTFROM")[0].textContent:"";

    result +=(getElements(permits[i], "nova", "NUMBERPARTTO")[0])? " - "+ getElements(permits[i], "nova", "NUMBERPARTTO")[0].textContent:"";

    result +="</td></tr><tr><td></td><td>";
    result += (getElements(permits[i], "nova", "ZIPCODE")[0])?getElements(permits[i], "nova", "ZIPCODE")[0].textContent+ " ":"" ;

    result += (getElements(permits[i], "nova", "MUNICIPALITYNL")[0])?getElements(permits[i], "nova", "MUNICIPALITYNL")[0].textContent:"";

    result += "</td></tr><tr><td>Onderwerp van de aanvraag :</td><td>";
    result += (getElements(permits[i], "nova", "OBJECTNL")[0])?getElements(permits[i], "nova", "OBJECTNL")[0].textContent+ " ":"";

    result += '</td><tr></tr><tr><td><a href="';
    result += (getElements(permits[i], "nova", "S_IDADDRESS")[0])?absolute_url+"/wawspublic_view?id=" + getElements(permits[i], "nova", "S_IDADDRESS")[0].textContent:"";

    result+= '">Meer informatie...<a/></td></tr></table></div>';
}
}

    result+= "</div>";
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



function applyDossierFilter(canceled,refused,demanded,granted){
    var cql = "";
    //create a cql filter based on the filter checkboxes
    if(canceled){
        cql += "STATUT_PERMIS IS NULL";
    }
    if(refused){
        if(cql == ""){
        cql += "STATUT_PERMIS = 'REFUSE'";
        }else{
            cql += " OR STATUT_PERMIS = 'REFUSE'";
        }
    }
    if(demanded){
        if(cql == ""){
        cql += "STATUT_PERMIS = 'DEMANDE'";
        }else{
            cql += " OR STATUT_PERMIS = 'DEMANDE'";
        }
    }
    if(granted){
        if(cql == ""){
        cql += "STATUT_PERMIS = 'OCTROYE'";
        }else{
            cql += " OR STATUT_PERMIS = 'OCTROYE'";
        }
    }
    if(cql == ""){
        cql = "STATUT_PERMIS IS NOT NULL AND STATUT_PERMIS <> 'REFUSE' AND STATUT_PERMIS <> 'DEMANDE' AND STATUT_PERMIS <> 'OCTROYE'";
    }
    //apply the cql filter
    dossiers.mergeNewParams({'CQL_FILTER': cql});
}

function searchAddress(street, number, post_code){

    var mypostrequest=new ajaxRequest();
    mypostrequest.onreadystatechange=function(){
        if (mypostrequest.readyState==4){
            if (mypostrequest.status==200 || window.location.href.indexOf("http")==-1){
                try{
                    var geo_response = eval( "(" + mypostrequest.responseText + ")" );
                    if(!geo_response.error){
                        if(geo_response.result)
                        {
                            var x =Number(geo_response.result[0].point.x);
                            var y =Number(geo_response.result[0].point.y);
                            if(!(isNaN(x) || isNaN(y)))
                            {
                                map.setCenter(new OpenLayers.LonLat(x,y), 6);
                            }
                        }else{
                            //no features found.alert user?

    }
}else{
    //error occured

    }
}catch(err){
    //handle exception?
}
}
else{
    alert("An error has occured making the request");
}
}
}

    var parameters="{'language': '"+ $('#current_language').html() +"','address': {'street': {'name':'"+street+"','postcode': '"+post_code+"'},'number': '"+number+"'}}";
    //TODO make a call to a proxy that can handle post requests
    var my_url = portal_url+"/wfs_post_request?url=http://services.gis.irisnetlab.be/urbis/Rest/Localize/getstreet&json=True"
    var ws_url = 'http://services.gis.irisnetlab.be/urbis/Rest/Localize/getstreet'
    //alert(my_url);
    mypostrequest.open("POST", my_url, true);
    mypostrequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    //mypostrequest.send("(" + parameters + ")");
    results = mypostrequest.send(parameters);
    //alert(results+" ------ "+my_url);.
    // bsuttor test
    $.ajax({
        type: "POST",
        url: ws_url,
        data: parameters,
        contentType: "application/json",
        dataType: "json",
        success:  function(data) {
            $('#results_panel').html('success<br />'+data+'<br />'+my_url+'<br />'+ parameters);
        },
        error:  function(data) {
            $('#results_panel').html('error <br />'+data+'<br />'+my_url+'<br />'+ parameters);
        },
    });
    

}

function ajaxRequest(){
    var activexmodes=["Msxml2.XMLHTTP", "Microsoft.XMLHTTP"]; //activeX versions to check for in IE
    if (window.ActiveXObject){ //Test for support for ActiveXObject in IE first (as XMLHttpRequest in IE7 is broken)
        for (var i=0; i<activexmodes.length; i++){
            try{
                return new ActiveXObject(activexmodes[i]);
            }
        catch(e){
            //suppress error
        }
        }
    }
    else if (window.XMLHttpRequest) // if Mozilla, Safari etc
        return new XMLHttpRequest();
    else
        return false;
}


function geocode(street, nbr, post_code) {    
    var ws = new jQuery.SOAPClient({
        url 		: "/WSGeoLoc", 
        methode 	: "getXYCoord", 
        data		: {
            language: "all",
            address: {
                street: {name: street, postCode: post_code},
                number: nbr
            }
        }, 
        async		: true, 
        success		: function(data, xml_data)
            {
                set_xy(data);
            }, 
        error		: function(sr)
            {
                if (console) console.log("error: " + sr); 
            }
        });
    ws.exec();
}

function set_xy(data) {
    coord_x = data.point.x;
    coord_y = data.point.y;
    point = new OpenLayers.LonLat(coord_x,coord_y);
    markers_layer.clearMarkers();
    markers_layer.addMarker(new OpenLayers.Marker(point));
    map.setCenter(point,5);
    filter_geom = new OpenLayers.Geometry.Point(coord_x,coord_y);
}


/*function set_result(data) {
    var absolute_url  = $('#absolute_url').html();
    var url = absolute_url+"/wawspublic_view?id=";
    var table = "<table class=\"urbis_result\"><tbody>";
    var header = "<tr>";
    var content = "<tr>";
    $.each(data, function(key, attribute) {
        if (key == "id") {
            header += "<th>" + key + "</th>";
            content += "<td><a href='"+url+attribute+"'>" + attribute + "</a></td>";

    }
    else {
        header += "<th>" + key + "</th>";
        content += "<td>" + attribute + "</td>";
    }
});    
table += header+'</tr>';
table += content+'</tr>';
table += "</tbody></table>";
$("#results_panel").html("Results <br />" + table);
}*/

/*function display(event) {
    var feature = event.feature;
    if (feature.cluster.length > 1) {
        if (map.getZoom() < 8) {
            map.setCenter(new OpenLayers.LonLat(feature.geometry.x, feature.geometry.y), map.getZoom()+2);
        }
    } else {
        set_result(feature.cluster[0].attributes);
    }
}*/

/*function showInfo(evt) {
    if (evt.features && evt.features.length) {
        highlightLayer.destroyFeatures();
        highlightLayer.addFeatures(evt.features);
        highlightLayer.redraw();
    } else {
        alert(evt.text);
    }
}*/
