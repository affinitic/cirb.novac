OpenLayers.DOTS_PER_INCH = 90.71428571428572;
OpenLayers.Util.onImageLoadErrorColor = 'transparent';
var map, layer;
var filter_geom;
var markers_layer, features_layer;
$(document).ready(function() {

    $("#accordion").accordion({active: 2});
    
    var url_ws_urbis = $('#ws_urbis').html();
    var url_ws_waws = $('#ws_waws').html();
    var json_file  = $('#json_file').html();
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
    map.addControl(new OpenLayers.Control.MousePosition({element: $('location')}));

    var urbislayer = new OpenLayers.Layer.WMS(
        "urbisFR",url_ws_urbis,
        {layers: 'urbisFR', format: 'image/png' },
        { tileSize: new OpenLayers.Size(256,256) }
    );
    map.addLayer(urbislayer);
    
    markers_layer = new OpenLayers.Layer.Markers( "Markers" );
    map.addLayer(markers_layer);
    
    var style = new OpenLayers.Style({
                    pointRadius: "${radius}",
                    fillColor: "#ffcc66",
                    fillOpacity: 0.8,
                    strokeColor: "#cc6633",
                    strokeWidth: "${width}",
                    strokeOpacity: 0.8
                }, {
                    context: {
                        width: function(feature) {
                            return (feature.cluster) ? 2 : 1;
                        },
                        radius: function(feature) {
                            var pix = 2;
                            if(feature.cluster) {
                                pix = Math.min(feature.attributes.count, 7) + 2;
                            }
                            return pix;
                        }
                    }
                });
    features_layer = new OpenLayers.Layer.Vector( "Features", {
                    strategies: [new OpenLayers.Strategy.BBOX(),
                                 new OpenLayers.Strategy.Cluster()],
                    protocol: new OpenLayers.Protocol.HTTP({
                        url: json_file,
                        format: new OpenLayers.Format.GeoJSON()
                        }),
                    styleMap: new OpenLayers.StyleMap({
                        "default": style,
                        "select": {
                            fillColor: "#8aeeef",
                            strokeColor: "#32a8a9"
                            }
                        })
                    });
    map.addLayer(features_layer);
    
    var select = new OpenLayers.Control.SelectFeature(
                    features_layer, {hover: false}
                );
    map.addControl(select);
    select.activate();
    features_layer.events.on({"featureselected": display});
    
    map.setCenter(new OpenLayers.LonLat(150000.0, 170000.0));
    $("#geocode").click(function() {
        geocode($("#street").val(), $("#number").val(), $("#post_code").val());        
    });
    
});

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
