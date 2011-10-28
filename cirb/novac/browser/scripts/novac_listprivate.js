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
    $('#key1').val('chKX');$('#key2').val('pTD8');$('#key3').val('9Nd8');
    $('#key4').val('rB58');$('#key5').val('OoyH');$('#key6').val('9w==');

});
