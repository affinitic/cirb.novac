$(document).ready(function() {
    var destTable = $("#dossier_list");
    $('#activate_key').click(function () {        
        var key = $('#key1').val()+$('#key2').val()+$('#key3').val()+$('#key4').val()+$('#key5').val()+$('#key6').val();        
        var url = $('#absolute_url').html()+'/activate_key?key='+key;                
        $.get(url, function(data) {
            //reload table with the new 'dossier'
            reload_table_list_dossier();
            $('#key1').val('');$('#key2').val('');$('#key3').val('');
            $('#key4').val('');$('#key5').val('');$('#key6').val('');
        });
        return false;
    });
    
    $("input").keyup(function () {
        var maxLength = $(this).attr('maxlength');
        if($(this).val().length == maxLength) {
            $(this).next().focus();
        }
    });
    //use in test 
    /*$('#key1').val('eipu');$('#key2').val('Z3lO');$('#key3').val('LuOd');
    $('#key4').val('aHiD');$('#key5').val('2+JY');$('#key6').val('Ag==');
    
    $('#key1').val('F6jL');$('#key2').val('7SHn');$('#key3').val('4Q90');
    $('#key4').val('I5kU');$('#key5').val('byLK');$('#key6').val('uQ==');
    */
});

function reload_table_list_dossier(){
    var url = $('#absolute_url').html()+'/get_table_lines_folder';        
    $.get(url, function(data) { 
        $('.content_list_folder').remove();
        $('table#dossier_list tr.title').after(data);
    });
}
