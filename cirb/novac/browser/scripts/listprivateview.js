$(document).ready(function() {
    var destTable = $("#dossier_list");
    $('#activate_key').click(function () {        
        var key = $('#key1').val()+$('#key2').val()+$('#key3').val()+$('#key4').val()+$('#key5').val()+$('#key6').val();        
        var url = '/activate_key?key='+key;                
        $.get(url, function(data) {
            //reload table with the new 'dossier'
            reload_table_list_dossier();
            $('#key1').val('');$('#key2').val('');$('#key3').val('');
            $('#key4').val('');$('#key5').val('');$('#key6').val('');
        });
        return false;
    });
    $("input#key1").bind('paste', function(e) {
        var el = $(this);
        setTimeout(function() {
            var text = $(el).val();
        if (text.length == 24) {
            $('#key1').val(text.substring(0,4));$('#key2').val(text.substring(4,8));$('#key3').val(text.substring(8,12));
            $('#key4').val(text.substring(12,16));$('#key5').val(text.substring(16,20));$('#key6').val(text.substring(20,24));
        } else {
            $('#key1').val(text.substring(0,4));
            $(this).next().focus();
        }
        }, 100);
    });
    $("input").keyup(function () {
        //var maxLength = $(this).attr('maxlength');        
        var maxLength = 4;
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
    //var url = $('#absolute_url').html()+'/get_table_lines_folder';
    var url = '/get_table_lines_folder';
    $.get(url, function(data) {
        $('.content_list_folder').remove();
        $('table#dossier_list tr.title').after(data);
    });
}
