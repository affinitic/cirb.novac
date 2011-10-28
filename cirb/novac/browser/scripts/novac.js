OpenLayers.DOTS_PER_INCH = 90.71428571428572;
OpenLayers.Util.onImageLoadErrorColor = 'transparent';
var map, layer;
var filter_geom;
var markers_layer, features_layer, highlightLayer;
$(document).ready(function() {



    $("#accordion").accordion({active: 2});
    
    var url_ws_urbis = $('#ws_urbis').html();
	var url_ws_urbis_cache = $('#urbis_cache_url').html();
    var url_ws_waws = $('#ws_waws').html();
    var json_file  = $('#json_file').html();
    var portal_url = $('#portal_url').html();
    url = portal_url+"/wfs_request?url="+url_ws_urbis+"&headers=";
   
    var mapOptions = { 
        resolutions: [34.76915808105469, 17.384579040527345, 8.692289520263673, 4.346144760131836, 2.173072380065918, 1.086536190032959, 0.5432680950164795, 0.2716340475082398, 0.1358170237541199],
        projection: new OpenLayers.Projection('EPSG:31370'),
        maxExtent: new OpenLayers.Bounds(16478.795,19244.928,301307.738,304073.87100000004),
        units: "meters", 
        theme: "++resource++cirb.novac.images/",
        controls: []
    };
    map = new OpenLayers.Map('map', mapOptions );

    map.addControl(new OpenLayers.Control.PanZoomBar({
            position: new OpenLayers.Pixel(2, 15)
    }));
    map.addControl(new OpenLayers.Control.Navigation());
    
    map.addControl(new OpenLayers.Control.Scale($('scale')));

	map.addControl(new OpenLayers.Control.LayerSwitcher() );


    var urbislayer = new OpenLayers.Layer.WMS(
        "urbisFR",url_ws_urbis,
        {layers: 'urbisFR', format: 'image/png' },
        { tileSize: new OpenLayers.Size(256,256) }
    );
    map.addLayer(urbislayer);
    
	var clusters = new OpenLayers.Layer.WMS("Clusters", url_ws_urbis, 			{layers: 'nova:CLUSTER3KM', transparent: 'true',minScale: 25000});
    map.addLayer(clusters);

	var points = new OpenLayers.Layer.WMS("Points",url_ws_urbis, 			{layers: 'nova:NOVA_DOSSIERS', transparent: 'true',maxScale: 25000});
    map.addLayer(points);

	highlightLayer = new OpenLayers.Layer.Vector("Highlighted Features", {
        displayInLayerSwitcher: false, 
        transparent: 'true'
        }
    );
   map.addLayer(highlightLayer);
		
	var click= new OpenLayers.Control.WMSGetFeatureInfo({
        url: url_ws_urbis, 
        title: 'Identify features by clicking',
        layers: [points],
        queryVisible: true
    });

	click.events.register("getfeatureinfo", this, showInfo);
    map.addControl(click); 
	click.activate();
            
    map.setCenter(new OpenLayers.LonLat(150000.0, 170000.0));
 
    
});

function showInfo(evt) {
        if (evt.features && evt.features.length) {
             highlightLayer.destroyFeatures();
             highlightLayer.addFeatures(evt.features);
             highlightLayer.redraw();
        } else {
            alert(evt.text);
        }
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


function set_result(data) {
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
}

function display(event) {
    var feature = event.feature;
    if (feature.cluster.length > 1) {
        if (map.getZoom() < 8) {
            map.setCenter(new OpenLayers.LonLat(feature.geometry.x, feature.geometry.y), map.getZoom()+2);
        }
    } else {
        set_result(feature.cluster[0].attributes);
    }
}
