var map;

var Milk = {};


var goldStar = {
    path : 'M 125,5 155,90 245,90 175,145 200,230 125,180 50,230 75,145 5,90 95,90 z',
    fillColor : "yellow",
    fillOpacity : 0.8,
    scale : 0.1,
    strokeColor : "gold",
    strokeWeight : 14
};

var showPosition = function(position) {
    var userLatLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    var marker = new google.maps.Marker({
        icon : goldStar,
        position : userLatLng,
        title : 'Your Location',
        map : map
    });
};

function contentwindow(views){
	var contentString = Mustache.render('<div align="right" dir="rtl" id=content>'+
	'<p align="center" id="name"><b>{{name}}</b></p>'+
	'<P id="address"><b>כתובת: </b>{{address}}</P>'+
	'<p id="city"><b>ישוב: </b>{{city}}</p>'+
	'<p id="phone"><b>טלפונים: </b>{{phones}}</p>'+
	'<table>'+
		'<tr colspan="2">'+
			'<td><b>שעות פעילות: </b></td>'+
		'</tr>'+
		'<tr>'+
			'<td>יום ראשון: </td>'+
			'<td id="sunday">{{days.sunday}}</td>'+
		'</tr>'+
		'<tr>'+
			'<td>יום שני: </td>'+
			'<td id="monday">{{days.monday}}</td>'+
		'</tr>'+
		'<tr>'+
			'<td>יום שלישי: </td>'+
			'<td id="tuesday">{{days.tuesday}}</td>'+
		'</tr>'+
		'<tr>'+
			'<td>יום רביעי: </td>'+
			'<td id="wednsday">{{days.wednsday}}</td>'+
		'</tr>'+
		'<tr>'+
			'<td>יום חמישי: </td>'+
			'<td id="thursday">{{days.thursday}}</td>'+
		'</tr>'+
		'<tr>'+
			'<td>יום שישי: </td>'+
			'<td id="friday">{{days.friday}}</td>'+
		'</tr>'+
	'</table>'+
	'<p><b>הערות:</b><br>{{notes}}</p>'+
'</div>', views);
	return contentString;
}


var infowindow = new google.maps.InfoWindow({
});

function processGeoJSON(results) {

    Milk.geojson = results;

    var markers = [];
    
	function doMarker(inlatlng, views){
		var marker = new google.maps.Marker({map: map, position: inlatlng, clickable: true});
 
		marker.info = new google.maps.InfoWindow({
		  	//content: desc
		});
		
		google.maps.event.addListener(marker, 'click', function() {
		infowindow.close();
	    infowindow.setContent(contentwindow(views));
	    infowindow.open(map, marker);
		});
 
	return marker;
}	
    for (var i = 0; i < results.features.length; i++) {
        var content = results.features[i].properties;
        var coords = results.features[i].geometry.coordinates;
        var latLng = new google.maps.LatLng(coords[1], coords[0]);
        
        var views = {
        	name : content.name,
        	address: content.address,
        	city: content.city,
        	phones: content.phones,
        	days: {
        		sunday: content.days[0],
        		monday: content.days[1],
        		tuesday: content.days[2],
        		wednsday: content.days[3],
        		thursday: content.days[4],
        		friday: content.days[5],
        	},
       		notes: content.notes,
       		owner: content.owner
        };
        var marker = doMarker(latLng, views);
		marker.setMap(map);
        markers.push(marker);
    }
   // var markerCluster = new MarkerClusterer(map, markers);

};

function initialize() {

    var mapOptions = {
        zoom : 7,
        center : new google.maps.LatLng(31.046051, 34.851612),
        mapTypeId : google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
	//------------------------------------------
	$.get('milk.geojson', {}, processGeoJSON, 'json');
	  
	  
    if (navigator.geolocation) {
        browserSupportFlag = true;
        navigator.geolocation.getCurrentPosition(function(position) {
            initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            map.setCenter(initialLocation);
            map.setZoom(17);

            showPosition(position);

        }, function() {
            handleNoGeolocation(browserSupportFlag);
        });
    }
    // Browser doesn't support Geolocation
    else {
        browserSupportFlag = false;
        handleNoGeolocation(browserSupportFlag);
    }

    function handleNoGeolocation(errorFlag) {
        // // TODO: maybe nothing
        // if (errorFlag == true) {
            // alert("Geolocation service failed.");
            // initialLocation = newyork;
        // } else {
            // alert("Your browser doesn't support geolocation. We've placed you in Siberia.");
            // initialLocation = siberia;
        // }
        // map.setCenter(initialLocation);
    }
}


$(initialize);