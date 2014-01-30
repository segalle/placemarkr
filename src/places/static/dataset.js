"use strict";

var dataset_map;
var dataset_data;

$(function() {
	$.get('dataset.json', function(data) {
			dataset_data = data;
		});

	$("#map-view-button").click(function() {
		$.get('datasetMap.html', function(data) {
			$("#dataset-content").empty().html(data);
			initMap();
			addMarkers(dataset_map);
			fitBounds(dataset_map,dataset_data);
		});
	});
	$("#list-view-button").click(function() {
		$.get('datasetList.html', function(data) {
			$("#dataset-content").empty().html(data);
		});
	});
	$("#album-view-button").click(function() {
		$.get('datasetAlbum.html', function(data) {
			$("#dataset-content").empty().html(data);
		});
	});

	//$("#list-view-button").addClass("active");
	//$("#map-view-button").removeClass("active");

	//$("#list-view-button").button('toggle');
	//$("#list-view-button").button('toggle');

	//$(".btn-group > .btn").click(function() {
	//	$(".btn-group > .btn").removeClass("active");
	//	$(this).addClass("active");
	//});
});

function initMap() {
	var mapOptions = {
		zoom : 8,
		mapTypeId : google.maps.MapTypeId.ROADMAP,
		center : new google.maps.LatLng(32, 34)
	};

	dataset_map = new google.maps.Map(document.getElementById('dataset_map'), mapOptions);
}

function addMarkers(map) {
	for(var i=0 ; i < dataset_data.length ; i++) {
		var place = dataset_data[i];
		if (!place.lat || !place.lng)
			continue;
		var inlatlng = new google.maps.LatLng(place['lat'], place['lng']);
		dataset_data[i].marker = new google.maps.Marker({
			map : map,
			position : inlatlng,
			clickable : true,
			icon : 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=' + i + '|FF0000|000000'
		});
	}
}

function fitBounds(map,dataset){
		var latlngbounds = new google.maps.LatLngBounds();
		
		for (var i=0; i< dataset.length; i++){
			latlngbounds.extend(dataset[i].marker.position);
		}
		
		map.fitBounds(latlngbounds);
		var blistener = google.maps.event.addListener(map, 'bounds_changed', function(event) {
		if (this.getZoom() > 15) {
			this.setZoom(15);
		}
		google.maps.event.removeListener(blistener);
	});
}

