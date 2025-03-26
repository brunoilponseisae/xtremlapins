let showOnlyAvailable=true
function switchNotAvailable() {
    const el = document.getElementById("listeLapins");
    showOnlyAvailable = !showOnlyAvailable
    if (showOnlyAvailable)
        el.classList.add('availableOnly');
    else
        el.classList.remove('availableOnly');
}