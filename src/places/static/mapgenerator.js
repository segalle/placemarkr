var map, infowindow, geocoder;

var Placemarkr = {
	markers : []
};

var ForeignPlacemarkr = {
	markers : []
};

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

	if (marker.place.vote != null){
		if (marker.place.vote == true){
			el.find('.votefor').attr('disabled', 'disabled');
		}
		else{
			el.find('.voteagainst').attr('disabled', 'disabled');
		}
	};
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

	var litem = $(Mustache.render('<li class="place list-group-item"><a href="#">{{forcount}}. {{address}}, {{city}}</a></li>', place));
	litem.data("marker", marker);
	marker.place = place;
	marker.litem = litem;
	$("#mainlist").append(litem);
	google.maps.event.addListener(marker, 'click', function() {
		showInfoWindow(marker);
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
		$.post('/addplacemark/', {
			place : Placemarkr.id,
			city : fulladdress["locality"],
			address : fulladdress["address"],
			lat : marker.getPosition().lat(),
			lng : marker.getPosition().lng()
		}, function(resp){  //if got response 200 from server
			if (resp == "OK"){
				$('#loading').text("Marker Created Successfuly");
				$('button').addClass('hide');
			}
			else {
				$('#loading').text("Marker already exists");
			}
			infowindow.close();
			infowindow.open(map, marker);
		});
	});
	
	el.find('.remove').on("click",function(){
		var idx = ForeignPlacemarkr.markers.indexOf(marker);
		console.log(idx);
		ForeignPlacemarkr.markers.splice(idx,1);
		marker.setMap(null);
		console.log(marker);
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

	var litem = $(Mustache.render('<li class="foreignplace list-group-item"><a href="#">{{forcount}}. {{address}}, {{city}}</a></li>', fulladdress));
	litem.data("marker", marker);
	litem.data("fulladdress", fulladdress);
	marker.place = result;
	$("#foreignlist").append(litem);
	google.maps.event.addListener(marker, 'click', function() {
		foreignInfoWindow(marker, fulladdress, litem);
	});

	return marker;
}

function codeAddress() {
	geocoder = new google.maps.Geocoder();
	var fulladdress = {
		address : document.getElementById("address").value,
		locality : document.getElementById("city").value,
	};

	geocoder.geocode({
		'address' : fulladdress['address']
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

	var forcount = 1;
	for (var i = 0; i < Placemarkr.placemarks.length; i++) {
		places[i]['forcount'] = forcount;
		var marker = doMarker(places[i]);
		Placemarkr.markers.push(marker);
		forcount += 1;
	}

	$('#jsontitle').click(function() {
		console.log("title");
		$("#jsoncontent").toggle();
	});

	//events for the main list

	$("li.place").hover(function() {
		var marker = $(this).data("marker");
		marker.setAnimation(google.maps.Animation.BOUNCE);
	}, function() {
		var marker = $(this).data("marker");
		marker.setAnimation(google.maps.Animation.none);
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
		},
		mouseleave : function() {
			var marker = $(this).data("marker");
			marker.setAnimation(google.maps.Animation.none);
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
