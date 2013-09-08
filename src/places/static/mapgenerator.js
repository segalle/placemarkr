var map, infowindow;

var Placemarkr = {
	markers : []
};

function showInfoWindow(marker) {
	
	console.log(marker, marker.place);
	
	marker.setAnimation(google.maps.Animation.none);
	
	if (infowindow) {
		infowindow.close();
	}
	infowindow = new google.maps.InfoWindow({});

	var s = Mustache.render("<p>{{address}}, {{city}}</p>" + "<input type='button' class='btn btn-default' value='True' />" + "<input type='button' class='btn btn-default' value='False' />", marker.place);
	infowindow.setContent(s);
	infowindow.open(map, marker);
	
	return marker;
}

function doMarker(place) {
	var inlatlng = new google.maps.LatLng(place['lat'], place['lng']);
	var marker = new google.maps.Marker({
		map : map,
		position : inlatlng,
		clickable : true
	});

	var litem = $(Mustache.render('<li class="place"><a href="#">{{address}}, {{city}}</a></li>', place));
	litem.data("marker", marker);
	marker.place = place;
	$("#mainlist").append(litem);
	google.maps.event.addListener(marker, 'click', function() {
		showInfoWindow(marker);
	});

	return marker;
}

function initialize() {

	var places = $(Placemarkr.placemarks);
	var pageid = $(id)[0];
	var mapOptions = {
		zoom : 7,
		center : new google.maps.LatLng(31.046051, 34.851612),
		mapTypeId : google.maps.MapTypeId.ROADMAP
	};

	map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);

	for (var i = 0; i < Placemarkr.placemarks.length; i++) {
		if (places[i]["id"] == pageid) {
			var marker = doMarker(places[i]);
			Placemarkr.markers.push(marker);

		}
	}

	$('#jsontitle').click(function() {
		$("#jsoncontent").toggle();
	});
	$("li.place").hover(function() {
		var marker = $(this).data("marker");
		marker.setAnimation(google.maps.Animation.BOUNCE);
	}, function() {
		var marker = $(this).data("marker");
		marker.setAnimation(google.maps.Animation.none);
	});

	$("li.place").click(function() {
		var marker = $(this).data("marker");
		showInfoWindow(marker);

	});

}

$(initialize);
