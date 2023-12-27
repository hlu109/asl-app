function togglePopup(id) {
    var profile_popup = document.getElementById(id);
    profile_popup.classList.toggle("show");
}

window.onload = function () {
    // add global click-handler to close popup when you click anywhere outside it
    const popups = [...document.getElementsByClassName('popup')];
    window.addEventListener('click', ({ target }) => {
        // ignore if we clicked the popup toggle button
        const popup_button = target.closest('.popup_button');
        console.log('popup_button', popup_button);

        // TODO: we have to check the associated popup that the toggle controls
        if (popup_button == null) {

            // check if we clicked inside a popup - if so, we want that one to remain visible
            const popup = target.closest('.popup');
            const clickedOntogglePopup = popup && popup.classList.contains('show');

            // toggle all the popups off except the open popup that we may have clicked
            popups.forEach(p => p.classList.remove('show'));
            if (clickedOntogglePopup) popup.classList.add('show');
        }
    });
}