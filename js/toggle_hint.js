function toggle_hint() {
    el = document.getElementById('hint').innerHTML = "aaaaaaaaa"
    // console.log("sdjfbskdjfbsdjkfabskjfasdfjhkasd fdjf as")

    if (el.style.visibility == 'hidden') {
        el.style.visibility = 'visible';
    } else {
        el.style.visibility = 'hidden';
    };
    el.innerHTML = "new updated text";

}
