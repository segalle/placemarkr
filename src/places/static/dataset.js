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
			fitBounds(dataset_map, dataset_data);
		});
	});
	$("#list-view-button").click(function() {
		$.get('datasetList.html', function(data) {
			$("#dataset-content").empty().html(data);
			$( "tr" ).css("cursor","pointer");
			$(function() {
				$("tr").click(function() {
					window.location = $(this).data('value');
				});
			});
		});
	});
	$("#album-view-button").click(function() {
		$.get('datasetAlbum.html', function(data) {
			$("#dataset-content").empty().html(data);
			$(".thumbnail" ).css("cursor","pointer");
			$(function() {
				$(".thumbnail").click(function() {
					window.location = $(this).data('value');
				});
			});
		});
	});

	$("#list-view-button").click();

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
	var infowindow = new google.maps.InfoWindow({});
	
	
	for (var i = 0; i < dataset_data.length; i++) {
		var place = dataset_data[i];
		if (!place.lat || !place.lng)
			continue;
		var inlatlng = new google.maps.LatLng(place['lat'], place['lng']);
		dataset_data[i].marker = new google.maps.Marker({
			map : map,
			position : inlatlng,
			clickable : true,
			title: dataset_data[i].title,
			icon : 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=' + dataset_data[i].vendor_id + '|FF0000|000000'
		});
		
		dataset_data[i].marker.data = dataset_data[i];
		
		google.maps.event.addListener(dataset_data[i].marker, 'click', function() {
			var content = getInfoWindowContent($(this)[0].data);
			infowindow.setContent(content);
		    infowindow.open(map,$(this)[0]);
		});
	}
}

function getInfoWindowContent(data) {
	var content = "<div id=\"infoWindowContent\" class=\"media\">";
	content += "<a class=\"pull-right\" href=\"" + data.url + "\">";
    content += "<img class=\"media-object\" src=\"" + data.imageUrl + "\" alt=\"Missing image\" width=\"70\" height=\"70\" >";
  	content += "</a>";
  	content += "<div class=\"media-body\">";
	content += "<h4 class=\"media-heading\" style=\"margin-top: 0px;\">" + data.title + "</h4>";
	content += "<h5>" + data.address + ", " + data.city + "</h5>";
	content += "<span style=\"font-size: 11px; margin-left: 5px;\">סה\"כ מיקומים <span class=\"badge\" style=\"font-size: 11px;\">" + data.numberOfPlacemarks + "</span></span>";
	content += "<span style=\"font-size: 11px;\">סה\"כ הצבעות <span class=\"badge\" style=\"font-size: 11px;\">" + data.numberOfVotes + "</span></span>";
	content += "</div>";
	//content += "<a href=\"#\" class=\"btn btn-primary\" role=\"button\">לפרטים</a>";
	content += "</div>";
	return content;
}

function fitBounds(map, dataset) {
	var latlngbounds = new google.maps.LatLngBounds();

	for (var i = 0; i < dataset.length; i++) {
		if (dataset[i].marker)
			latlngbounds.extend(dataset[i].marker.position);
		else
			console.log("marker " + i + " is not defined.");
	}

	map.fitBounds(latlngbounds);
	var blistener = google.maps.event.addListener(map, 'bounds_changed', function(event) {
		if (this.getZoom() > 15) {
			this.setZoom(15);
		}
		google.maps.event.removeListener(blistener);
	});
}

