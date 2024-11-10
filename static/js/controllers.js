function toggleWaterPump() {
    const toggle = document.getElementById("toggleWaterPump");
    var controlCard = document.getElementById("water-control");
    if (toggle.checked) {
        controlCard.style.backgroundColor = "#12807c";
        controlCard.querySelector("p strong").textContent = "ON";
        forwardCommandToFlask("/on_water_pump");
    } else {
        controlCard.style.backgroundColor = "#C2D6C5";
        controlCard.querySelector("p strong").textContent = "OFF";
        forwardCommandToFlask("/off_water_pump");
    }
}

function toggleFertilizerPump() {
    const toggle = document.getElementById("toggleFertilizerPump");
    var controlCard = document.getElementById("fertilizer-control");
    if (toggle.checked) {
        controlCard.style.backgroundColor = "#12807c";
        controlCard.querySelector("p strong").textContent = "ON";
        forwardCommandToFlask("/on_fertilizer_pump");
    } else {
        controlCard.style.backgroundColor = "#C2D6C5";
        controlCard.querySelector("p strong").textContent = "OFF";
        forwardCommandToFlask("/off_fertilizer_pump");
    }
}

function toggleRoof() {
    const toggle = document.getElementById("toggleRoof");
    var controlCard = document.getElementById("roof-control");
    if (toggle.checked) {
        controlCard.style.backgroundColor = "#12807c";
        controlCard.querySelector("p strong").textContent = "OPEN";
        forwardCommandToFlask("/open_roof");
    } else {
        controlCard.style.backgroundColor = "#C2D6C5";
        controlCard.querySelector("p strong").textContent = "CLOSED";
        forwardCommandToFlask("/close_roof");
    }
}

async function forwardCommandToFlask(command) {
    try {
        const response = await fetch(command, { method: 'GET' });
        const data = await response.json();
        console.log(data.message);
    } catch (error) {
        console.error('Error:', error);
    }
}