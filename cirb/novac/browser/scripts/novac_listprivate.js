$(document).ready(function() {
    var destTable = $("#dossier_list");
    $('#activate_key').click(function () {
        
        var key = $('#key1').val()+$('#key2').val()+$('#key3').val()+$('#key4').val()+$('#key5').val()+$('#key6').val();        
        var url = $('#absolute_url').html()+'/activate_key?key='+key;        
        $.get(url, function(data) {
            //reload table with the new 'dossier'
            reload_table_list_dossier();
        });
        return false;
    });
    $('#activate_key').click(function () { 
        
        return false;
    });
    
    
    $("input").keyup(function () {
        var maxLength = $(this).attr('maxlength');
        if($(this).val().length == maxLength) {
            $(this).next().focus();
        }
    });
    //used for test 
    /*$('#key1').val('eipu');$('#key2').val('Z3lO');$('#key3').val('LuOd');
    $('#key4').val('aHiD');$('#key5').val('2+JY');$('#key6').val('Ag==');
    */
    $('#key1').val('d6kR');$('#key2').val('UTy/');$('#key3').val('8Fbz');
    $('#key4').val('KcLE');$('#key5').val('j4Dy');$('#key6').val('dg==');
    
});

function reload_table_list_dossier(){
    var url = $('#absolute_url').html()+'/get_table_lines_folder';        
    $.get(url, function(data) {
        $("#content_list_folder").replaceWith(data);  
    });
}
