function doOnsubmit() {
    $('a').click(function (e) {
        e.preventDefault();
    });
    document.querySelector("#search > input").disabled = true;
    document.getElementById("showWait").innerHTML = '<strong style="color:#FF0080;">' + "&emsp;查詢中請稍等" + "</strong>";
    return true;
}


function doOnsubmitCancel() {
    $('a').click(function (e) {
        e.preventDefault();
    });
    $('input').click(function (e) {
        e.preventDefault();
    });
    document.querySelector("#search > input").disabled = true;
    document.getElementById("showWait").innerHTML = '<strong style="color:#FF0080;">' + "&emsp;訂單取消中請稍等" + "</strong>";
    return true;
}