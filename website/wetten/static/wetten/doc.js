// Do necessary bindings.
$(document).ready( function() {

// This binds all clicks in the metalex view to update the related information.
$('root').bind('click', function(e){
	console.log('Click fired');
	var target = $(e.target);
	
	// Get "about" value from clicked element. This URI is used to determine its
	// name in the citation network and retrieve the desired information.
	var about = target.attr("about");
	if (about) {
		getRelated(about);
	}
	else {
		console.log('Undefined');
	}
});

// Bind elements with class "result".
bindResults();

// Update page width (layout) when browser window size changes.
$(window).on('resize', function(){
	setWidth()
});

// Set the width according to browser window after document is ready
setWidth()

});


function bindCloseDetails() {
    $('#close_details').bind('click', function(){
	    hideDetails();
    });

}

// Update layout of selected result and show details (metalex data) for that result.
function bindResults() {
    $('.result').bind('click', function(e){
        // Get the clicked result element.
        var target = $(e.target);
        
        // Change the style of the previously selected result back to normal.
        $('.selected_result').addClass('result');
        $('.selected_result').removeClass('selected_result');
        
        // Change the style of the new element to that of a selected one.
        target.removeClass('result');
        target.addClass('selected_result');
        
        // Show (load) the details for the entity to which the selected result belongs.
        showDetails(target.attr('entity'));
    });
}

// Adapt the width of the page's elements to the width of the browser window.
function setWidth() {
    // Get window width.
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

// Loads relevant internal and external articles for clicked entity.
function getRelated(entity) {
	console.log('Getting related for: ' + entity);
	
	// Show that data is being retrieved.
	$('#internal').html('<b style="color:green">Gegevens laden...</b>');
	$('#external').html('<b style="color:green">Gegevens laden...</b>');
	
	// Perform ajax get request.
	$.get('/wetten/related/', {'entity': entity}, function(data) {
  		data = JSON.parse(data);
  		if (data['success']) {
  		    // Populate the views
  			$('#internal').html(data['internal']);
  			$('#external').html(data['external']);
  			
  			// Bind the new result elements to the click event.
		    bindResults();
  		}
  		else {
  			alert('Er is geen data gevonden.');
  		}
	});
}

// Loads and shows the content of the selected result.
function showDetails(entity) {
    // Show the view and change the metalex container's height.
	$('#result_details').show();
	$('#root_container').height(380);
	
	// Show that data is being loaded.
	$('#result_details').html('<b style="color:green">Gegevens laden...</b>');
	
	// Perform ajax get request.
	$.get('/wetten/relatedContent/', {'entity': entity}, function(data) {
  		$('#result_details').html(data);
  		// Scroll to top.
  		$('#result_details').scrollTop(0);
	    bindCloseDetails();
	});
	
}

// Hides the details view and restores the original metalex view to full height
function hideDetails() {
	$('#result_details').hide();
	$('#root_container').height(775);
}
