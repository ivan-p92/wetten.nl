$(document).ready( function() {

$('root').bind('click', function(e){
	console.log('Click fired');
	var target = $(e.target);
	var about = target.attr("about");
	if (about) {
		getRelated(about);
	}
	else {
		console.log('Undefined');
	}
});

$('#close_details').bind('click', function(){
	hideDetails();
});

bindResults();

$(window).on('resize', function(){
	setWidth()
});

setWidth()

});

function bindResults() {
    $('.result').bind('click', function(e){
        var target = $(e.target);
        $('.selected_result').addClass('result');
        $('.selected_result').removeClass('selected_result');
        target.removeClass('result');
        target.addClass('selected_result');
    
        showDetails();
    });
}

function setWidth() {
	var w = $(window).width();
	
	if (w < 1100) {
	    $('#info_container').width(300);
	    var metalex = w - 400;
	    metalex = (metalex < 300) ? 300: metalex;
	    var diff = 700 - metalex;
	    $('#root_container, #result_details').width(metalex);
	    $('#info_container').css('left', (800-diff) + 'px');
	}
	else {
	    var info = w - 800;
        info = (info < 300)? 300: info;
        $('#root_container, #result_details').width(700);
        $('#info_container').width(info);
        $('#info_container').css('left', '800px');
    }
}

function getRelated(entity) {
	console.log('Getting related for: ' + entity);
	$('#internal').html('<b style="color:green">Gegevens laden...</b>');
	$('#external').html('<b style="color:green">Gegevens laden...</b>');
	
	$.get('/wetten/related/', {'entity': entity}, function(data) {
  		//$('#ajax_result').html(data);
  		data = JSON.parse(data);
  		if (data['success']) {
  			$('#internal').html(data['internal']);
  			$('#external').html(data['external']);
		    bindResults();
  		}
  		else {
  			alert('Er is geen data gevonden.');
  		}
	});
}

function showDetails() {
	$('#result_details').show();
	$('#root_container').height(400);
}

function hideDetails() {
	$('#result_details').hide();
	$('#root_container').height(810);
}
