OpenLayers.DOTS_PER_INCH = 90.71428571428572;
OpenLayers.Util.onImageLoadErrorColor = 'transparent';
var map, layer;
var filter_geom;
var markers_layer, features_layer;
$(document).ready(function() {
    /*var url_ws_waws = $('#ws_waws').html();
    var folder_id = $('#folder_id').html();
    var url = "https://ws.irisnetlab.be/nova/pub/dossiers/";
    called_url = url+folder_id;
    
    result= $.getJSON(  
                called_url, 
                function(json) {  
                    var result = "Language code is  "+ json.responseData.language;  
                   alert(result);}) */
    //alert(called_url + " : "+result);
    var url_ws_urbis = $('#ws_urbis').html();
    var portal_url = $('#portal_url').html();
    var x = $('#x').html();
    var y = $('#y').html();
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
    
    var icon_url = portal_url+'/++resource++cirb.novac.images/marker.png';
    alert(icon_url);
    var size = new OpenLayers.Size(21,25);
    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
    var icon_marker = new OpenLayers.Icon(icon_url, size, offset);
    var size = new OpenLayers.Size(21,25);
    address_folder = new OpenLayers.LonLat(x, y);
    markers_layer = new OpenLayers.Layer.Markers( "Markers" );
    markers_layer.addMarker(new OpenLayers.Marker(address_folder), icon_marker);
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
    
    map.setCenter(address_folder, 5);
    
    
});
