// full screen map
var mapId = document.getElementById("map");
function fullScreenView() {
  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    mapId.requestFullscreen();
  }
}

// leaflet browser print function
L.control.browserPrint({ position: "topright" }).addTo(map);

//leaflet search
L.Control.geocoder().addTo(map);

// leaflet measure
L.control
  .measure({
    primaryLengthUnit: "kilometer",
    secondaryLengthUnit: "meter",
    primaryAreaUnit: "sqmeters",
    secondaryAreaUnit: undefined,
  })
  .addTo(map);

// zoom layer for the view
$(".zoom-to-layer").click(function () {
  map.setView([21.0, 78.0], 5);
});
