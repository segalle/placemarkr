var map;

var Placemarkr = {
	markers: []
};

var infowindow = new google.maps.InfoWindow({});

function generateInfoWindow(info_content){
	var info_window_content = Mustache.render("<p>{{address}}, {{city}}</p>"+
	"<input type='button' class='btn btn-default' value='True' />"+
	"<input type='button' class='btn btn-default' value='False' />"
	,info_content);
	return info_window_content;
}

function doMarker(inlatlng, info_content){
	var marker = new google.maps.Marker({map: map, position: inlatlng, clickable: true});
 
	infowindow.setContent(generateInfoWindow(info_content));
	google.maps.event.addListener(marker, 'click', function() {
	infowindow.close();
    infowindow.open(map, marker);
	});
 
	return marker;
}	

function initialize() {

	var mapOptions = {
		zoom : 7,
		center : new google.maps.LatLng(31.046051, 34.851612),
		mapTypeId : google.maps.MapTypeId.ROADMAP
	};

	map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);

	var locations = $(places);
	for (var i = 0; i < locations.length; i++) {
		var myLatlng = new google.maps.LatLng(locations[i][1], locations[i][0]);
		console.log(myLatlng);
		
		var info_content = {
			city : locations[i][2],
			address: locations[i][3]
		};
		
 		var marker = doMarker(myLatlng, info_content);
 		
		Placemarkr.markers.push(marker);
		
		console.log(locations[i]);
	}
	
		
	$('#jsontitle').click(function() {
		$("#jsoncontent").toggle();
	});
	$("li[id^='place']").hover(function() {
		current = $("li").index(this);
		Placemarkr['markers'][current].setAnimation(google.maps.Animation.BOUNCE);
		
		$(this).addClass('highlighted');
	}, function() {
		Placemarkr['markers'][current].setAnimation(google.maps.Animation.none);
		$(this).removeClass('highlighted');
	});
	
	$("li[id^='place']").click(function(){
		current = $("li").index(this);
		infowindow.open(map, Placemarkr['markers'][current]);
		Placemarkr['markers'][current].setAnimation(google.maps.Animation.none);
	});
		
}

$(initialize); 