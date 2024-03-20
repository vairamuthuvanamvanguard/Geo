// map class initialize
var map = L.map("map").setView([21.0, 78.0], 5);
map.zoomControl.setPosition("topright");

// adding osm titlelayer
var osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);
var transportLayer = L.tileLayer('https://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=8743d4fe145049a58fac8e102620488c', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &amp; <a href="https://www.thunderforest.com/maps/transport/">Thunderforest</a>'
}).addTo(map);
var Esri_NatGeoWorldMap = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}",
  {
    attribution:
      "Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC",
    maxZoom: 16,
  }
);

var CartoDB_DarkMatter = L.tileLayer(
  "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
  {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: "abcd",
    maxZoom: 20,
  }
);

// Addng marker in the center of the map
var singlemarker = L.marker([20.5937, 78.9629])
  .addTo(map)
  .bindPopup("A pretty CSS popup.<br> Easily customizable.")
  .openPopup();

// add map scale
L.control.scale({ position: "bottomright" }).addTo(map);

//  mouse co-ordinates
map.on("mousemove", function (e) {
  $(".coordinate").html(
    `Latitute: ${e.latlng.lat} Longitutde:${e.latlng.lng} `
  );
});

// Geojson load
var marker = L.markerClusterGroup();
var taji = L.geoJSON(data, {
  onEachFeature: function (feature, layer) {
    layer.bindPopup(feature.properties.name);
  },
});
taji.addTo(marker);
marker.addTo(map);

var baseMaps = {
  OSM: osm,
  "World Map": Esri_NatGeoWorldMap,
  "Light Map": CartoDB_DarkMatter,
  "Transport Map":transportLayer
};

var overlayMaps = {
  "GeoJson Markers": marker,
  singlemarker: singlemarker,
};

L.control
  .layers(baseMaps, overlayMaps, { collapsed: false, position: "topleft" })
  .addTo(map);
