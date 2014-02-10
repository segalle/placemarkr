"use strict";

var map, infowindow, geocoder;

var forcount = 0;

var Placemarkr = {
	markers : []
};

var ForeignPlacemarkr = {
	markers : []
};

function clear_foreign_markers() {
	for (var p = 0; p < ForeignPlacemarkr['markers'].length; p++) {
		ForeignPlacemarkr['markers'][p].setMap(null);
	}
};

function vote_buttons_enable_disable(marker, el) {
	if (marker.place.vote != null) {
		if (marker.place.vote == true) {
			el.find('.votefor').attr('disabled', 'disabled');
			el.find('.voteagainst').removeAttr('disabled');
		} else {
			el.find('.voteagainst').attr('disabled', 'disabled');
			el.find('.votefor').removeAttr('disabled');
		}
	};
}

function fitBounds(map, markers){
		var latlngbounds = new google.maps.LatLngBounds();
		
		for (var i=0; i< markers.length; i++){
			latlngbounds.extend(markers[i].position);
		}
		
		map.fitBounds(latlngbounds);
		var blistener = google.maps.event.addListener(map, 'bounds_changed', function(event) {
		if (this.getZoom() > 15) {
			this.setZoom(15);
		}
		google.maps.event.removeListener(blistener);
	});
}

function voteIcon(marker) {
	if (marker.vote != undefined) {
		var s = marker.vote ? 'up' : 'down';
		return '<span class="badge pull-left"><span class="glyphicon glyphicon-thumbs-' + s + '"></span></span>';
	} else {
		return "";
	};
}

function showInfoWindow(marker) {
	marker.setAnimation(google.maps.Animation.none);

	if (infowindow) {
		infowindow.close();
	}
	infowindow = new google.maps.InfoWindow({});

	var s = ich.iw(marker.place)

	var el = $(s);

	infowindow.setContent(el.get(0));
	infowindow.open(map, marker);

	vote_buttons_enable_disable(marker, el);

	el.find(".vote").on("click", function() {
		$('#loading').removeClass('hide');
		var button = $(this);
		$.post('/vote/', {
			id : marker.place.id,
			positive : $(this).val()
		}, function(resp) {
			if (resp == "OK") {
				console.log("OK", this);
				$('#loading').text("Vote Recieved");
				$(button).attr('disabled', 'disabled');
			} else {
				$('#loading').text("Updated");
				marker.place.vote = !marker.place.vote;
				marker.thumbicon = voteIcon(marker.place);
				console.log(marker.litem[0]);
				marker.litem.find(".badge").replaceWith(marker.thumbicon);
				console.log(marker);
				vote_buttons_enable_disable(marker, el);

			}
			infowindow.close();
			infowindow.open(map, marker);
		});
	});
	return marker;
}

function doMarker(place) {

	var inlatlng = new google.maps.LatLng(place['lat'], place['lng']);
	var marker = new google.maps.Marker({
		map : map,
		position : inlatlng,
		clickable : true,
		icon : 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=' + place['forcount'] + '|FF0000|000000'
	});

	place.icon = voteIcon(place);

	var litem = $(Mustache.render('<li class="place list-group-item">' + place.icon + '<a href="#">{{forcount}}. {{address}}, {{city}}</a></li>', place));
	litem.data("marker", marker);
	marker.place = place;
	marker.litem = litem;
	$("#mainlist").append(litem);
	google.maps.event.addListener(marker, 'click', function() {
		showInfoWindow(marker);
	});

	google.maps.event.addListener(marker, 'mouseover', function() {
		litem.addClass('markerlist');
	});

	google.maps.event.addListener(marker, 'mouseout', function() {
		litem.removeClass('markerlist');
	});

	return marker;
}

function foreignInfoWindow(marker, fulladdress, litem) {
	marker.setAnimation(google.maps.Animation.none);
	if (infowindow) {
		infowindow.close();
	}
	infowindow = new google.maps.InfoWindow({});

	var s = ich.fiw(fulladdress);
	var el = $(s);

	infowindow.setContent(el.get(0));
	infowindow.open(map, marker);

	el.find(".vote").on("click", function() {
		$('#loading').removeClass('hide');

		forcount += 1;
		var place = {
			city : fulladdress["locality"],
			address : fulladdress["address"],
			lat : marker.getPosition().lat(),
			lng : marker.getPosition().lng(),
			vote : true,
			forcount : forcount
		};
		$.post('/addplacemark/', {
			place : Placemarkr.id,
			city : place['city'],
			address : place["address"],
			lat : place['lat'],
			lng : place['lng']
		}, function(resp) {//if got response 200 from server
			if (resp == "exists") {
				$('#loading').text("Marker already exists");
				return;
			}
			$('#loading').text("Marker Created Successfuly");
			$('button').addClass('hide');
			$('#foreignlist').empty();
			clear_foreign_markers();
		});
		place.id = Number(resp);
		doMarker(place);

		infowindow.close();
		infowindow.open(map, marker);
	});

	el.find('.remove').on("click", function() {
		var idx = ForeignPlacemarkr.markers.indexOf(marker);
		ForeignPlacemarkr.markers.splice(idx, 1);
		marker.setMap(null);
		litem.detach();
	});

	return marker;
}

function createForeignMarker(result, fulladdress) {
	var marker = new google.maps.Marker({
		map : map,
		position : result.geometry.location,
		clickable : true,
		icon : 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=' + fulladdress['forcount'] + '|006400|ffffff'
	});

	var litem = ich.cfm(fulladdress);

	litem.data("marker", marker);
	litem.data("fulladdress", fulladdress);
	marker.place = result;
	$("#foreignlist").append(litem);
	google.maps.event.addListener(marker, 'click', function() {
		foreignInfoWindow(marker, fulladdress, litem);
	});
	google.maps.event.addListener(marker, 'mouseover', function() {
		litem.addClass('foreignmarkerlist');
	});

	google.maps.event.addListener(marker, 'mouseout', function() {
		litem.removeClass('foreignmarkerlist');
	});

	return marker;
}

function updateStreetView(marker) {
	
	var panoramaOptions = {
	    position: marker.getPosition(),
	    pov: {
	      heading: 94,
	      pitch: 10
	    }
  	};
	var panorama = new  google.maps.StreetViewPanorama(document.getElementById('pano'),panoramaOptions);
	map.setStreetView(panorama);
}

function codeAddress() {
	geocoder = new google.maps.Geocoder();
	var fulladdress = {
		address : document.getElementById("address").value,
		locality : document.getElementById("city").value,
	};

	var a = fulladdress['address'] + " " + fulladdress['locality'];
	geocoder.geocode({
		'address' : a,
	}, function(results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			var forcount = 1;
			for (var i = 0; i < results.length; i++) {
				fulladdress["forcount"] = forcount;
				var marker = createForeignMarker(results[i], fulladdress);
				ForeignPlacemarkr.markers.push(marker);
				forcount += 1;	
				if (i == 0)
					updateStreetView(marker);
			};
			
			fitBounds(map, ForeignPlacemarkr.markers);
		} else {
			alert("לא נמצא מיקום עבור הכתובת והעיר. שגיאה: " + status);
		}
	});
}

function initialize() {

	var places = $(Placemarkr.placemarks);
	var pageid = $(Placemarkr.id);
	var mapOptions = {
		mapTypeId : google.maps.MapTypeId.ROADMAP,
		streetViewControl: false
	};

	map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);

	for (var i = 0; i < Placemarkr.placemarks.length; i++) {
		forcount += 1;
		places[i]['forcount'] = forcount;
		var marker = doMarker(places[i]);
		Placemarkr.markers.push(marker);
	}
	fitBounds(map, Placemarkr.markers);

	$('#jsontitle').click(function() {
		$("#jsoncontent").toggle();
	});

	//events for the main list

	$("li.place").hover(function() {
		var marker = $(this).data("marker");
		updateStreetView(marker);
		marker.setAnimation(google.maps.Animation.BOUNCE);
		$(this).addClass('markerlist');
	}, function() {
		var marker = $(this).data("marker");
		marker.setAnimation(google.maps.Animation.none);
		$(this).removeClass('markerlist');
	});

	$("body").on("click", "li.place", function() {
		var marker = $(this).data("marker");
		showInfoWindow(marker);
	});

	// events for the foreign list

	$("body").on({
		mouseenter : function() {
			var marker = $(this).data("marker");
			updateStreetView(marker);
			marker.setAnimation(google.maps.Animation.BOUNCE);
			$(this).addClass('foreignmarkerlist');
		},
		mouseleave : function() {
			var marker = $(this).data("marker");
			marker.setAnimation(google.maps.Animation.none);
			$(this).removeClass('foreignmarkerlist');
		}
	}, "li.foreignplace");

	$("body").on("click", "li.foreignplace", function() {
		var marker = $(this).data("marker");
		var fulladdress = $(this).data("fulladdress");
		foreignInfoWindow(marker, fulladdress, $(this));
	});

	$("#searchform").submit(function() {
		$('#foreignlist').empty();
		clear_foreign_markers();
		codeAddress();
		return false;
	});
	
	var fenway = new google.maps.LatLng(0,0);
	
	if (Placemarkr.markers[0])
		fenway = Placemarkr.markers[0].getPosition();
	
	var panoramaOptions = {
	    position: fenway,
	    pov: {
	      heading: 94,
	      pitch: 10
	    }
  	};
	var panorama = new  google.maps.StreetViewPanorama(document.getElementById('pano'),panoramaOptions);
	map.setStreetView(panorama);
}

function generateTableContent(data) {
	if (!data.length)
		return "<p>לא נמצאו הצבעות</p>";	
	
	var content = "<table class=\"table\"><thead><tr>";
	content += "<th class=\"text-right\">#</th>";
	content += "<th class=\"text-right\">שם</th>";
	content += "<th class=\"text-right\">תאריך</th>";
	content += "</tr></thead>";

	for (var i=0; i < data.length ; i++) {
    	content += "<tr>";
        content += "<td>" + i + "</td>";
		content += "<td><a href=\"" + data[i].url + "\">" + data[i].first_name + " " + data[i].last_name + " (" + data[i].username + ")</a></td>";
		content += "<td>לפני " + data[i].date + "</td>";
    	content += "</tr>";
	}
	
	content += "</table>";
	return content;
}

$(function() {
	initialize();

	$('#votingTableButton').data("visible",false);
	
	$('#votingTableButton').click(function() {	
		if ($('#votingTableButton').data("visible")) {
			$('#votingTableButton').popover("hide");
			$('#votingTableButton').data("visible",false);			
		}
		else {
	       	$.get('votingTable.json', function(data) {
				var content = generateTableContent(data);
				$('#votingTableButton').popover('destroy');
				$('#votingTableButton').popover({title: 'הצבעות אחרונות', 
										content: content, 
									  	trigger: 'manual',
									  	html:true});
				$('#votingTableButton').popover("show");
				$('#votingTableButton').data("visible",true);	
			});	
		}
	 });
});
