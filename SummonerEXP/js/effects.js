$(document).ready(function(){
    $('#calculate').click(function(){
        $('#showEXPListButton, #nextStep').show();
    });
    
    $('#showEXPListButton').click(function(){
        $('#EXPTable').toggle();
    });
    
    $('#calculateTime').click(function() {
       $('#resultEnergyDetails').fadeIn(); 
    });
});