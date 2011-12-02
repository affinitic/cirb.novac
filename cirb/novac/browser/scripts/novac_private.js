var targetID="";
$(document).ready(function() {
    
    $('#add_mandat').click(function () {        
        var mandat = $('#input_mandat').val();
        targetID = getURLParameter('id');
        var url = $('#absolute_url').html()+'/activate_mandat?mandat='+mandat+'&targetID='+targetID;
        $.get(url, function(data) {
            //reload table with the new 'secondary key'
            reload_table_list_secondary_key();
        });
        return false;
    });
    
    $('.revoke_mandat').click(function () {
        targetID = getURLParameter('id');
        var url = $(this).attr("href");
        $(this).attr("href","#");
        $.get(url, function(data) {
            //reload table with the new 'secondary key'
            reload_table_list_secondary_key();
        });
        return false;
    }); 
    
    map_init();
    
});

function reload_table_list_secondary_key(){
    var url = $('#absolute_url').html()+'/get_table_lines_secondary_keys?targetID='+targetID;
    $.get(url, function(data) {        
        $('.secondary_key').remove();
        $('table#secondary_keys tr.title').after(data);
    });
}

function getURLParameter(name) {
    return decodeURI((RegExp(name + '=' + '(.+?)(&|$)').exec(location.search) || [,null])[1]);
}
