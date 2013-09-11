"use strict";

var map, infowindow, geocoder;

var forcount = 0;

var Placemarkr = {
	markers : []
};

var ForeignPlacemarkr = {
	markers : []
};

function vote_buttons_enable_disable(marker, el){
	if (marker.place.vote != null){
		if (marker.place.vote == true){
			el.find('.votefor').attr('disabled', 'disabled');
			el.find('.voteagainst').removeAttr('disabled');
		}
		else{
			el.find('.voteagainst').attr('disabled', 'disabled');
			el.find('.votefor').removeAttr('disabled');
		}
	};
}

function voteIcon(marker){
	console.log("markervote", marker.vote)
	if (marker.vote != undefined) {
		var s = marker.vote ? 'up' : 'down';
				return '<span class="badge pull-left"><span class="glyphicon glyphicon-thumbs-'+ s +'"></span></span>';
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

	var s = Mustache.render("<div><p>{{address}}, {{city}}</p>" + "<button id='votefor' class='btn btn-default vote votefor' value='True'>נכון</button>" +
	 "<button id='voteagainst' class='btn btn-default vote voteagainst' value='False'>לא נכון</button>"+
	 "<div id='loading' class='hide'>Loading...</div></div>" 
	 , marker.place);
	 
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
			if (resp == "OK"){
				console.log("OK", this);
				$('#loading').text("Vote Recieved");
				$(button).attr('disabled', 'disabled');   
			}
			else{
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
		icon: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld='+place['forcount']+'|FF0000|000000'
	});
	
	place.icon = voteIcon(place);

	var litem = $(Mustache.render('<li class="place list-group-item">'+place.icon+'<a href="#">{{forcount}}. {{address}}, {{city}}</a></li>', place));
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

	var s = Mustache.render("<div><p>{{address}}, {{locality}}?</p>" + "<button class='btn btn-default vote' value='True'>נכון</button>" + 
	"<button class='btn btn-default remove' value='False'>הסר</button>"+
	"<span id='loading' class='hide'>Loading...</span></div>", fulladdress);

	var el = $(s);
	
	infowindow.setContent(el.get(0));
	infowindow.open(map, marker);

	el.find(".vote").on("click", function() {
		$('#loading').removeClass('hide');
		
		forcount += 1;
		var place = {
			city: fulladdress["locality"],
			address : fulladdress["address"],
			lat : marker.getPosition().lat(),
			lng : marker.getPosition().lng(),
			vote: true,
			forcount: forcount
		};
		$.post('/addplacemark/', {
			place : Placemarkr.id,
			city : place['city'],
			address : place["address"],
			lat : place['lat'],
			lng : place['lng']
		}, function(resp){  //if got response 200 from server
			if (resp == "exists"){
				$('#loading').text("Marker already exists");
				return;
			}
			
			$('#loading').text("Marker Created Successfuly");
			$('button').addClass('hide');
			$('#foreignlist').empty();
			marker.setMap(null);
			place.id = Number(resp);
			doMarker(place);

			infowindow.close();
			infowindow.open(map, marker);
		});
	});
	
	el.find('.remove').on("click",function(){
		var idx = ForeignPlacemarkr.markers.indexOf(marker);
		ForeignPlacemarkr.markers.splice(idx,1);
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
		icon: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld='+fulladdress['forcount']+'|006400|ffffff'
	});

	var litem = $(Mustache.render('<li class="foreignplace list-group-item"><a href="#">{{forcount}}. {{address}}, {{locality}}</a></li>', fulladdress));
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

function codeAddress() {
	geocoder = new google.maps.Geocoder();
	var fulladdress = {
		address : document.getElementById("address").value,
		locality : document.getElementById("city").value,
	};

	var a = fulladdress['address']+ " " + fulladdress['locality'];
	geocoder.geocode({
		'address' : a,
	}, function(results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			map.setCenter(results[0].geometry.location);
			var forcount = 1;
			for (var i = 0; i < results.length; i++) {
				fulladdress["forcount"] = forcount;
				var marker = createForeignMarker(results[i], fulladdress);
				ForeignPlacemarkr.markers.push(marker);
				forcount += 1;
			};
		} else {
			alert("Geocode was not successful for the following reason: " + status);
		}
	});
}

function initialize() {

	var places = $(Placemarkr.placemarks);
	var pageid = $(Placemarkr.id);
	var mapOptions = {
		zoom : 7,
		center : new google.maps.LatLng(31.046051, 34.851612),
		mapTypeId : google.maps.MapTypeId.ROADMAP
	};

	map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);

	
	for (var i = 0; i < Placemarkr.placemarks.length; i++) {
		forcount += 1;
		places[i]['forcount'] = forcount;
		var marker = doMarker(places[i]);
		Placemarkr.markers.push(marker);
		
	}

	$('#jsontitle').click(function() {
		console.log("title");
		$("#jsoncontent").toggle();
	});

	//events for the main list

	$("li.place").hover(function() {
		var marker = $(this).data("marker");
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
		console.log("search");
		codeAddress();
		return false;
	});

}

$(initialize);
