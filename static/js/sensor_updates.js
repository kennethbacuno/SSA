function showSection(sectionId) {
    document.getElementById('npk-updates').style.display = 'none';
    document.getElementById('sensor-updates').style.display = 'none';
    document.getElementById(sectionId).style.display = 'block';
}

async function fetchWaterUpdates() {
    try {
        const response = await fetch('/water_level');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        document.getElementById("water-level").textContent = `Water Level: ${data.water_level} %`;

    } catch (error) {
        console.error('Fetch error:', error);
    }
}
setInterval(fetchWaterUpdates, 1000);
