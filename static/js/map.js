const map = L.map('map').setView([20.0, 78.0], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let boundary;
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);
const drawControl = new L.Control.Draw({
  draw: {
    polyline: false,
    rectangle: false,
    circle: false,
    marker: false,
    circlemarker: false,
    polygon: true
  },
  edit: { featureGroup: drawnItems }
});
map.addControl(drawControl);

map.on('draw:created', function (event) {
  if (boundary) drawnItems.removeLayer(boundary);
  boundary = event.layer;
  drawnItems.addLayer(boundary);
});

document.getElementById('saveBoundary').onclick = async () => {
  if (!boundary) return alert('Draw a polygon first!');
  const coords = boundary.getLatLngs()[0].map(p => [p.lat, p.lng]);
  const res = await fetch('/boundary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ coordinates: coords })
  });
  const data = await res.json();
  if (data.status === 'ok') window.location = '/inputs';
};