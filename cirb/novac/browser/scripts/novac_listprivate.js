$(document).ready(function() {
    var destTable = $("#dossier_list");
    $('#activate_key').click(function () {
        
        var key = $('#key1').val()+$('#key2').val()+$('#key3').val()+$('#key4').val()+$('#key5').val()+$('#key6').val();        
        var url = $('#absolute_url').html()+'/activate_key?key='+key;        
        $.get(url, function(data) {
            var newRow = $("<tr><td>"+data+"</td><td></td><td></td><td></td></tr>");
          
            destTable.append(newRow);
        });
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
