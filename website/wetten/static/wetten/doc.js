var versionScope = 'alinea';
var latestEntity = '';

// Do necessary bindings.
$(document).ready( function() {

// This binds all clicks in the metalex view to update the related information.
$('root').bind('click', function(e){
	var target = $(e.target);
	
	// Get "about" value from clicked element. This URI is used to determine its
	// name in the citation network and retrieve the desired information.
	var about = target.attr("about");
	
	if (about) {
        // Check if user clicked on title of law or somewhere in considerans
        if (about.indexOf("intitule") != -1 || 
            about.indexOf("considerans") != -1 ||
            about.indexOf("wij") != -1) {
            console.log('Het is intitule of considerans');
            var bwbExpr = new RegExp("http://doc.metalex.eu/id/BWBR\\d{7}");
            var bwbMatch = bwbExpr.exec(about);
            console.log(bwbMatch);
            if (bwbMatch) {
                about = bwbMatch[0];
            }
            latestEntity = about;
            getRelated(about);
            $('#timetravel').html('Zie versie-informatie boven geraadpleegde wet.');
	    }
	    else {
	        latestEntity = about;
            getRelated(about);
            getVersions(target, target, 1);
        }
	}
	else {
		console.log('Undefined');
	}
});

// Bind the switching of sorting method.
$('#sort_methods div').bind('click', function(e) {
    var target = $(e.target);
    $('#sort_methods div').removeClass('selected_sort');
    switch (target.attr('id')) {
        case "method0":
            target.addClass('selected_sort');
            showSortMethod(0);
            break;
        case "method1":
            target.addClass('selected_sort');
            showSortMethod(1);
            break;
        case "method2":
            target.addClass('selected_sort');
            showSortMethod(2);
            break;
        default:
            $('#method0').addClass('selected_sort');
            showSortMethod(0);
            break;
    }
});

$('#versions_popup').bind('click', function() {
    $('#versions_popup').hide();
});

$('#focus_version_picker').bind('click', function() {
    $('#detail_versions').hide();
    $('#focus_versions').show();
    $('#versions_popup').show();
});

$('#detail_version_picker').bind('click', function() {
    $('#detail_versions').show();
    $('#focus_versions').hide();
    $('#versions_popup').show();
});

// When user clicks on current selection item in drop down menu, collapse it to
// cancel highlight.
$('#current_selection').bind('click', function() {
    $('#menubar').children('li:nth-child(3)').superfish('hide'); 
});

// Superfish for dropdown menu
$('#menubar').superfish({
	//add options here if required
});

// Bind the close button.
$('#close_button').bind('click', function() {
    hideDetails();
});

// Bind references in metalex data
bindRefs();

// Bind elements with class "result" and the timetravel results
bindResults();

// Update page width (layout) when browser window size changes.
$(window).on('resize', function(){
	setWidth()
});

// Set the width according to browser window after document is ready
setWidth()

// Bind click on maximum number of results option
$('.maxResultSetter').bind('click', function(e) {
    var target = $(e.target);
    var maxResults = target.attr('number');
    setCookie('maxResults', maxResults, 7);
    if (maxResults == '0') {
        $('#maxResultsInfo').html('Aantal resultaten (nu: alle)');
    }
    else {
        $('#maxResultsInfo').html('Aantal resultaten (nu: ' + maxResults + ')');
    }
    loadEntitiesForBWB();
    getRelated(latestEntity);
});

checkMaxResultsCookie();

// Bind hover on options menu to show latest cookie setting for maxResults
$('#options').mouseenter(function() {
    var maxResults = getCookie('maxResults');
    if (maxResults == '0') {
        $('#maxResultsInfo').html('Aantal resultaten (nu: alle)');
    }
    else {
        $('#maxResultsInfo').html('Aantal resultaten (nu: ' + maxResults + ')');
    }
});

loadEntitiesForBWB();

});

/////////////////////
// End of binds
/////////////////////


// Load entities for bwb
function loadEntitiesForBWB() {
    var maxResults = getCookie('maxResults');
    $('.important_for_bwb').html('<b style="color:green">Gegevens laden...</b>');
    
    // Perform ajax get request.
	$.get('/wetten/bwb/', {'maxResults': maxResults}, function(data) {
  		data = JSON.parse(data);
  		    // Populate the views
  			$('#imp0').html(data['inDegree']);
  			$('#imp1').html(data['degreeCentrality']);
  			$('#imp2').html(data['betweenness']);
  			
  			// Bind the new result elements to the click event.
		    bindResults();
	});
}

// Show results for chosen ordering
function showSortMethod(method) {
    $('.important_for_bwb, .internal, .external').hide();
    switch (method) {
        case 0:
            $('.sort0').show();
            break;
        case 1:
            $('.sort1').show();
            break;
        case 2:
            $('.sort2').show();
            break;
        default:
            $('.sort0').show();
            break;
    }
}

function setVersionScope(setting) {
    
    versionScope = setting;
    
    if (versionScope == 'artikel') {
        alert('Als u nu op een artikel (of hoger niveau, b.v. hoofdstuk) klikt,\n krijgt u '+
            'alle bestaande versies te zien in het "Tijdreizen"\n venster. Wilt u wijzigingen ' + 
            'van individuele alinea\'s\n bekijken, kies dan voor "Alinea niveau".');
    }
    else if (versionScope == 'alinea') {
        alert('Als u nu op een tekst element (b.v. alinea) klikt, krijgt u in het\n' +
              '"Tijdreizen" venster versies te zien van de betreffende tekst die\n' +
              'inhoudelijk verschillen van de geraadpleegde versie.');
    }
    
    // Collapse the menu item.
    $('#menubar').children('li:nth-child(2)').superfish('hide');
}


// Bind intrefs and extrefs
function bindRefs() {
    // First unbind to avoid multiple calls after clicking on reference
    $('.intref, .extref').unbind();
    $('.intref, .extref').bind('click', function(e) {
        // Don't register as click in parent elements
        e.stopPropagation();
        
        var about = $(e.target).attr('about');
        if (about) {
            loadReferenceContent(about);
        }
        else {
            alert('Deze link werkt niet');
        }
    });
}

// Update layout of selected result and show details (metalex data) for that result.
function bindResults() {
    // First unbind all.
    $('.result').unbind();
    $('.result span').unbind();
    $('.result_title').unbind()
    
    $('.result').bind('click', function(e){
        console.log('.result action fired');
        // Get the clicked result element.
        var target = $(e.target);
        
        // Change the style of the previously selected result back to normal.
        $('.selected_result').addClass('result');
        $('.selected_result').removeClass('selected_result');
        
        // Change the style of the new element to that of a selected one.
        target.removeClass('result');
        target.addClass('selected_result');
        
        // Show (load) the details for the entity to which the selected result belongs.
        if (target.hasClass('v_result')) {
            var expression = target.attr('expression');
            detailVersionsTimetravel();
            loadMetalexData(expression);
        }
        else {
            showDetails(target.attr('entity'));
        }
    });
    
    // Bind result span. If span is clicked, act like result is clicked
    $('.result span').bind('click', function(e){
        e.stopPropagation();
        // Get the clicked result_title element.
        var target = $(e.target);
        var result = target.parent();
        
        // Change the style of the previously selected result back to normal.
        $('.selected_result').addClass('result');
        $('.selected_result').removeClass('selected_result');
        
        // Change the style of the new element to that of a selected one.
        result.removeClass('result');
        result.addClass('selected_result');
        
        // Show (load) the details for the entity to which the selected result belongs.
        if (result.hasClass('v_result')) {
            var expression = result.attr('expression');
            detailVersionsTimetravel();
            loadMetalexData(expression);
        }
        else {
            showDetails(result.attr('entity'));
        }
    });
    
    // Bind result title. If title clicked, act like parent result is clicked
    $('.result_title').bind('click', function(e){
        e.stopPropagation();
        // Get the clicked result_title element.
        var target = $(e.target);
        var result = target.parent().parent();
        
        // Change the style of the previously selected result back to normal.
        $('.selected_result').addClass('result');
        $('.selected_result').removeClass('selected_result');
        
        // Change the style of the new element to that of a selected one.
        result.removeClass('result');
        result.addClass('selected_result');
        
        // Show (load) the details for the entity to which the selected result belongs.
        if (result.hasClass('v_result')) {
            var expression = result.attr('expression');
            detailVersionsTimetravel();
            loadMetalexData(expression);
        }
        else {
            showDetails(result.attr('entity'));
        }
    });
}

function bindDetailVersions() {
    $('.d_version').unbind();
    $('.d_version').bind('click', function(e) {
        var target = $(e.target);
        if (!target.hasClass('skip')) {
            var dateMessage = $('.skip').html();
            dateMessage = dateMessage.replace(' – getoonde versie', '');
            $('.skip').html(dateMessage);
            $('.skip').removeClass('skip');
            target.addClass('skip');
            dateMessage = target.html();
            target.html(dateMessage + ' – getoonde versie');
            
            var dateInfo;
            if (target.index() == 0) {
                dateInfo = 'Getoonde versie: ' + dateMessage + ' – Dit is de nieuwste versie.';
            } 
            else {
                dateInfo = 'Getoonde versie: ' + dateMessage + ' – Let op: nieuwere versie beschikbaar!';
            }
            $('#detail_version_picker').html(dateInfo);
            loadMetalexData(target.attr('expression'));
        }
    });
}

// Adapt the width of the page's elements to the width of the browser window.
function setWidth() {
    // Get window width.
	var w = $(window).width();
	
	if (w < 1100) {
	    $('#info_container, #sort_methods').width(300);
	    var metalex = w - 400;
	    metalex = (metalex < 300) ? 300: metalex;
	    var diff = 700 - metalex;
	    $('#cs_li').width(480 - diff);
	    $('#current_selection').width(480 - diff - 10);	    
	    $('#root_container, #result_details').width(metalex);
	    $('#close_button').css('left', (metalex + 35) + 'px');
	    $('#info_container, #sort_methods').css('left', (800-diff) + 'px');
	}
	else {
	    var info = w - 800;
        info = (info < 300)? 300: info;
        $('#cs_li').width(480);
        $('#current_selection').width(470);
        $('#root_container, #result_details').width(700);
        $('#close_button').css('left', '735px');
        $('#info_container, #sort_methods').width(info);
        $('#info_container, #sort_methods').css('left', '800px');
    }
}

// Loads relevant internal and external articles for clicked entity.
function getRelated(entity) {
	console.log('Getting related for: ' + entity);
	
	// Show that data is being retrieved.
	$('.internal').html('<b style="color:green">Gegevens laden...</b>');
	$('.external').html('<b style="color:green">Gegevens laden...</b>');
	
	var maxResults = getCookie('maxResults');
	// Perform ajax get request.
	$.get('/wetten/related/', {'entity': entity, 'maxResults': maxResults}, function(data) {
  		data = JSON.parse(data);
  		if (data['success']) {
  		    // Populate the views
  			$('.internal.sort0').html(data['internal']['inDegree']);
  			$('.internal.sort1').html(data['internal']['degreeCentrality']);
  			$('.internal.sort2').html(data['internal']['betweenness']);
  			$('.external.sort0').html(data['external']['inDegree']);
  			$('.external.sort1').html(data['external']['degreeCentrality']);
  			$('.external.sort2').html(data['external']['betweenness']);
  			$('#current_selection').html('Selectie: ' + data['current_selection']);
  			
  			// Bind the new result elements to the click event.
		    bindResults();
  		}
  		else {
  			$('.internal').html('<b style="color:green">Geen citatie gegevens beschikbaar.</b>');
	        $('.external').html('<b style="color:green">Geen citatie gegevens beschikbaar.</b>');
            $('#current_selection').html('Selectie: ' + data['current_selection']);
  		}
	});
}

// Loads data for given reference
function loadReferenceContent(about) {
    // Show the view and change the metalex container's height.
    $('#result_details').show();
    $('#close_button').show();
    $('#detail_version_picker').show();
    $('#root_container').height(350);

    // Show that data is being loaded.
    $('#result_details').html('<b style="color:green">Gegevens laden...</b>');

    // Perform ajax get request.
    $.get('/wetten/reference/', {'about': about}, function(data) {
        data = JSON.parse(data);
        $('#result_details').html(data['metalex']);
        // Scroll to top.
        $('#result_details').scrollTop(0);
        $('#detail_versions').html(data['versions']);
        $('#detail_version_picker').html(data['dateInfo']);
        bindRefs();
        bindDetailVersions();
    });
}

// Loads and shows the content of the selected result.
function showDetails(entity) {
    // Show the view and change the metalex container's height.
	$('#result_details').show();
    $('#close_button').show();
    $('#detail_version_picker').show();
	$('#root_container').height(350);
	
	// Show that data is being loaded.
	$('#result_details').html('<b style="color:green">Gegevens laden...</b>');
	
	// Perform ajax get request.
	$.get('/wetten/relatedContent/', {'entity': entity}, function(data) {
  		data = JSON.parse(data);
        $('#result_details').html(data['metalex']);
        // Scroll to top.
        $('#result_details').scrollTop(0);
        $('#detail_versions').html(data['versions']);
        $('#detail_version_picker').html(data['dateInfo']);
        bindRefs();
        bindDetailVersions();
	});
}

function loadMetalexData(expression) {
    // Show the view and change the metalex container's height.
	$('#result_details').show();
	$('#close_button').show();
    $('#detail_version_picker').show();
	$('#root_container').height(350);
	
	// Show that data is being loaded.
	$('#result_details').html('<b style="color:green">Gegevens laden...</b>');
	
	// Perform ajax get request.
	$.get('/wetten/metalexContent/', {'expression': expression}, function(data) {
  		$('#result_details').html(data);
  		// Scroll to top.
  		$('#result_details').scrollTop(0);
	    bindRefs();
	});
}

// Retrieves other versions for clicked part of document.
// |iteraton| ensures search for parent with li, lid or al class stops after a limit
function getVersions(target, originalTarget, iteration) {
    // Show that data is being retrieved.
	$('#timetravel').html('<b style="color:green">Gegevens laden...</b>');
	
	// Perform ajax get request for current version scope setting.
	if (versionScope == 'artikel') {
	    var about = target.attr('about');
        $.get('/wetten/timetravelArticle/', {'about': about}, function(data) {
            
            // Populate the view
            $('#timetravel').html(data);
        
            // Bind the new result elements to the click event.
            bindResults();
        });
    }
    else if (versionScope == 'alinea') {
        // Proceed if the current target element has one of the following classes:
        // li, lid or al.
        if (target.hasClass('al') || target.hasClass('li') || target.hasClass('lid')) {
            var about = target.attr('about');
            $.get('/wetten/timetravelParagraph/', {'about': about}, function(data) {
            
                var nb = '<div class="nb">NB: alleen inhoudelijk van elkaar verschillende versies getoond</div>';
                // Populate the view
                $('#timetravel').html(nb + data);
        
                // Bind the new result elements to the click event.
                bindResults();
            });
        }
        // Else take the parent class and call this function again, but only for a total
        // of 4 times.
        else if (iteration < 5){
            var parentTarget = target.parent();
            console.log('new parent');
            getVersions(parentTarget, originalTarget, iteration + 1);
        }
        // User has clicked on higher level element.
        else {
            var about = originalTarget.attr('about');
            // Get regular article or higher level source for original target.
            $.get('/wetten/timetravelArticle/', {'about': about}, function(data) {
            
                // Populate the view
                $('#timetravel').html(data);
        
                // Bind the new result elements to the click event.
                bindResults();
            });            
        }
    }
}

// Hides the details view and restores the original metalex view to full height
function hideDetails() {
	$('#result_details').hide();
	$('#close_button').hide();
	$('#detail_version_picker').hide()
	$('#root_container').height(745);
}

// Retrieve and set versions for clicked result
function detailVersionsTimetravel() {
    $('#detail_version_picker').html('Huidige versie: zie tijdreisvenster.');
    var div = '<div class="d_version skip">Zie tijdreisvenster</div>';
    $('#detail_versions').html(div);
}

// Functions for results cookie. The cookie that stores the preferred number of results to show.
function setCookie(c_name, value, exdays)
{
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var c_value = escape(value) + ((exdays==null) ? "" : "; expires="+exdate.toUTCString());
    document.cookie = c_name + "=" + c_value;
}

function getCookie(c_name)
{
    var c_value = document.cookie;
    var c_start = c_value.indexOf(" " + c_name + "=");
    if (c_start == -1)
    {
        c_start = c_value.indexOf(c_name + "=");
    }
    if (c_start == -1)
    {
        c_value = null;
    }
    else
    {
        c_start = c_value.indexOf("=", c_start) + 1;
        var c_end = c_value.indexOf(";", c_start);
        if (c_end == -1)
        {
            c_end = c_value.length;
        }
        c_value = unescape(c_value.substring(c_start,c_end));
    }
    return c_value;
}

function checkMaxResultsCookie()
{
    var maxResults = getCookie("maxResults");
    if (maxResults != null && maxResults != "")
    {
        console.log('preferred number of results: ' + maxResults);
    }
    else
    {
        setCookie('maxResults', '5', 7);
    }
}