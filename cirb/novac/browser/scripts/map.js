OpenLayers.DOTS_PER_INCH = 90.71428571428572;
OpenLayers.Util.onImageLoadErrorColor = 'transparent';
var map, layer;
var markers_layer, features_layer;

function map_init() {
    var url_ws_urbis = $('#ws_urbis').html();
    var url_ws_urbis_cache = $('#urbis_cache_url').html();
    portal_url = $('#portal_url').html();
    OpenLayers.ImgPath = portal_url+"/++resource++cirb.novac.images/";
    var x = $('#x').html();
    var y = $('#y').html();
    var mapOptions = {
        resolutions: [1112.61305859375, 556.306529296875, 278.1532646484375, 139.07663232421876, 69.53831616210938, 34.76915808105469, 17.384579040527345, 8.692289520263673, 4.346144760131836, 2.173072380065918, 1.086536190032959, 0.5432680950164795, 0.2716340475082398],
        projection: new OpenLayers.Projection('EPSG:31370'),
        maxExtent: new OpenLayers.Bounds(16478.795,19244.928,301307.738,304073.87100000004),
        units: "meters", 
        controls: [],
        theme: portal_url + "/++resource++cirb.novac.scripts/openlayers.css"
    };
    map = new OpenLayers.Map('map', mapOptions );
    
    map.addControl(new OpenLayers.Control.Navigation());
    
    var panel = new OpenLayers.Control.Panel();
    panel.addControls([new OpenLayers.Control.ZoomIn(), new OpenLayers.Control.ZoomOut()]);
    map.addControl(panel);
    
    //map.addControl(new OpenLayers.Control.Scale($('scale')));
    //map.addControl(new OpenLayers.Control.MousePosition({element: $('location')}));
    
    var matrixIds = new Array(16);
    for (var i=0; i<16; ++i) {
        matrixIds[i] = "EPSG:31370:" + i;
    }
    var ortho2009 = new OpenLayers.Layer.WMTS({
        name: "urbis ortho 2009",
        url: "http://geoserver.gis.irisnetlab.be/gwc/service/wmts",
        layer: "urbis:ortho2009",
        matrixSet: "EPSG:31370",
        matrixIds: matrixIds,
        serverResolutions: [1112.61305859375, 556.306529296875, 278.1532646484375, 139.07663232421876, 69.53831616210938, 34.76915808105469, 17.384579040527345, 8.692289520263673, 4.346144760131836, 2.173072380065918, 1.086536190032959, 0.5432680950164795, 0.2716340475082398, 0.1358170237541199, 0.06790851187705994, 0.03395425593852997],
        format: "image/png",
        style: "_null",
        opacity: 1,
        isBaseLayer: true
    });
    map.addLayer(ortho2009);
    
    var icon_url = portal_url+'/++resource++cirb.novac.images/map_pin.png';
    var size = new OpenLayers.Size(32,32);
    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
    var icon_marker = new OpenLayers.Icon(icon_url, size, offset);
    var address_folder = new OpenLayers.LonLat(x, y);
    markers_layer = new OpenLayers.Layer.Markers( "Markers" );
    markers_layer.addMarker(new OpenLayers.Marker(address_folder, icon_marker));
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
    
    map.setCenter(address_folder,11);
}