function showSection(sectionId) {
    document.getElementById('forecast').style.display = 'none';
    document.getElementById('form').style.display = 'none';
    document.getElementById(sectionId).style.display = 'block';
}