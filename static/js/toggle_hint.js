function toggle_hint() {
    el = document.getElementById("hint");
    if (el.style.visibility == "hidden") {
        el.style.visibility = "visible";
    } else {
        el.style.visibility = "hidden";
    }
}
