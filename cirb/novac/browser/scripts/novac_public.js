$(document).ready(function() {
    var url_ws_waws = $('#ws_waws').html();
    var folder_id = $('#folder_id').html();
    var url = "https://ws.irisnetlab.be/nova/pub/dossiers/";
    called_url = url+folder_id;
    
    /*result= $.getJSON(  
                called_url, 
                function(json) {  
                    var result = "Language code is  "+ json.responseData.language;  
                   alert(result);}) */
    //alert(called_url + " : "+result);
});
