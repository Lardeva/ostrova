function changeCssHide() {
    //If you want to hide the arrow absolutely,add this.
    var suitInput = document.getElementById('suit-left');
    suitInput.style.display = 'none';

    var wrap = document.getElementById('wrap');
    wrap.style.background = 'inherit';

    var suitCol = document.getElementsByClassName('suit-columns')[0];
    suitCol.style.paddingLeft = '0';
}

function changeCssShow() {
    //If you want to hide the arrow absolutely,add this.
    var suitInput = document.getElementById('suit-left');
    suitInput.style.display = 'block';

    var wrap = document.getElementById('wrap');
    wrap.style.background = null;

    var suitCol = document.getElementsByClassName('suit-columns')[0];
    suitCol.style.paddingLeft = '190px';
}

function clickCounter() {

    if (document.getElementById('myButton').firstChild.data == "Скрий Меню") {
        document.getElementById('myButton').firstChild.data = "Покажи Меню";
        changeCssHide();
    }
    else {
        document.getElementById('myButton').firstChild.data = "Скрий Меню";
        changeCssShow();
    }

    //Use HTML5 browser session to store the show/hide session, bu using the name of the link as flag
    sessionStorage.menuMark = document.getElementById('myButton').firstChild.data;

}

$(function() {
    //reload the actual menu state from browser's session and display accordingly on document load
    document.getElementById('myButton').firstChild.data = sessionStorage.menuMark || "Скрий Меню";
    if (document.getElementById('myButton').firstChild.data == "Покажи Меню") {
        changeCssHide();
    } else {
        changeCssShow();
    }
});
