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
    $('#key1').val('kkZd');$('#key2').val('rP/R');$('#key3').val('2IbS');
    $('#key4').val('IB1/');$('#key5').val('bu+x');$('#key6').val('Hg==');

});
