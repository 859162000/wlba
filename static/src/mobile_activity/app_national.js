function toggles(ele){
    var data = ele.attr("data");
    if (!data) {
        ele.animate({height: "10rem"},600);
        ele.attr("data","1");
    } else {
        ele.animate({height: 0},600,'linear');
         ele.removeAttr("data");
    }
}
$("#rule").on("click", function () {
    toggles($("#rulebox"));
});

$("#btns").on("click", function () {
    toggles($("#rulebox3"));
});



