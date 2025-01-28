function fetchData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            const output = document.getElementById('data-output');
            output.innerHTML = `
                <p>Nome: ${data.name}</p>
                <p>Versione: ${data.version}</p>
                <p>Descrizione: ${data.description}</p>
            `;
        })
        .catch(error => console.error('Errore:', error));
}

// Inizializzazione della mappa con Leaflet
function initMap() {
    // Coordinate di Trento (Centro)
    var lat = 46.0677;
    var lon = 11.1216;

    // Crea una mappa centrata su Trento
    var map = L.map('map').setView([lat, lon], 14.2); // Zoom più ravvicinato

    // Aggiungi il layer della mappa
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Aggiungi i marker per le zone di parcheggio
    var parkingZones = {
        'Centro': { lat: 46.068, lon: 11.1216 },
        'Nord': { lat: 46.085, lon: 11.1216 },
        'Ovest': { lat: 46.062, lon: 11.114 },
        'Sud': { lat: 46.059, lon: 11.135 },
        'Est': { lat: 46.075, lon: 11.144 }
    };

    // Aggiungi i marker sulla mappa per ciascuna zona
    for (var zone in parkingZones) {
        var marker = L.marker([parkingZones[zone].lat, parkingZones[zone].lon]).addTo(map);
        marker.bindPopup("<b>" + zone + "</b><br><a href='javascript:void(0);' onclick='showParkingInfo(\"" + zone.toLowerCase() + "\")'>View Details</a>");
    }
}

// Funzione per mostrare i dettagli del parcheggio in una finestra popup
function showParkingInfo(zone) {
    // Crea una nuova finestra per visualizzare la tabella
    var newWindow = window.open("", "_blank", "width=800,height=600");

    // Definisci il contenuto HTML per la nuova finestra (la tabella)
    var content = "<html><head><title>Parcheggio " + zone.charAt(0).toUpperCase() + zone.slice(1) + "</title></head><body>";
    content += "<h2>Dettagli Parcheggio " + zone.charAt(0).toUpperCase() + zone.slice(1) + "</h2>";

    // Crea una tabella con i dettagli del parcheggio
    content += "<table border='1' cellpadding='10' cellspacing='0' style='border-collapse: collapse; width: 100%;'>";
    content += "<thead><tr><th>Posizione</th><th>Prezzo</th></tr></thead><tbody>";

    switch (zone) {
        case 'center':
            content += "<tr><td>Via Mazzini</td><td>€2/h</td></tr>";
            content += "<tr><td>Via S. Croce</td><td>€1.5/h</td></tr>";
            break;
        case 'north':
            content += "<tr><td>Via Trento Nord</td><td>€1/h</td></tr>";
            break;
        case 'west':
            content += "<tr><td>Via Trento Ovest</td><td>€1.5/h</td></tr>";
            break;
        case 'south':
            content += "<tr><td>Via Trento Sud</td><td>€1.2/h</td></tr>";
            break;
        case 'east':
            content += "<tr><td>Via Trento Est</td><td>€1.4/h</td></tr>";
            break;
        default:
            content += "<tr><td colspan='2'>Zona non trovata.</td></tr>";
            break;
    }

    content += "</tbody></table>";
    content += "<p><a href='javascript:window.close()'>Close window</a></p>";
    content += "</body></html>";

    // Scrivi il contenuto HTML nella nuova finestra
    newWindow.document.write(content);
    newWindow.document.close();
}




document.addEventListener("DOMContentLoaded", function() {
    // Chiamata AJAX per ottenere i dati del parcheggio
    fetch('/api/parking_data')
        .then(response => response.json())
        .then(data => {
            // Aggiorna la tabella dei parcheggi con i dati ricevuti
            const table = document.querySelector('.parking-table tbody');
            table.innerHTML = `
                <tr>
                    <td>${data.covered}</td>
                    <td>${data.free}</td>
                    <td>${data.occupied}</td>
                </tr>
            `;

            // Aggiorna l'istogramma con i dati dell'affluenza
            const affluenzaData = {
                labels: data.hours,
                datasets: [{
                    label: 'Parcheggi Occupati',
                    data: data.occupiedData,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Parcheggi Liberi',
                    data: data.freeData,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            };

            const config = {
                type: 'bar',
                data: affluenzaData,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Affluenza Oraria dei Parcheggi'
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Ore del Giorno'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Numero di Parcheggi'
                            },
                            beginAtZero: true
                        }
                    }
                }
            };

            const ctx = document.getElementById('parkingChart').getContext('2d');
            new Chart(ctx, config);
        });
});
