async function fetchDashboardUpdates() {
    try {
        const response = await fetch('/dashboard_updates');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();

        document.getElementById("db-nitrogen").textContent = `Nitrogen: ${data.nitrogen} mg/kg`;
        document.getElementById("db-phosphorus").textContent = `Phosphorus: ${data.phosphorus} mg/kg`;
        document.getElementById("db-potassium").textContent = `Potassium: ${data.potassium} mg/kg`;
        document.getElementById("db-soil-moisture").textContent = `Soil Moisture: ${data.soil_moisture}`;
        document.getElementById("db-water-level").textContent = `Water Level: ${data.water_level} %`;

    } catch (error) {
        console.error('Fetch error:', error);
    }
}
setInterval(fetchDashboardUpdates, 1000);