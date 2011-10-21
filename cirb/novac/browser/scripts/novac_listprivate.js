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

});
