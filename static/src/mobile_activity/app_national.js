function toggles(ele){
    var data = ele.attr("data");
    if (!data) {
        ele.animate({height: "11.8rem"},600);
        ele.attr("data","1");
    } else {
        ele.animate({height: 0},600,'linear');
         ele.removeAttr("data");
    }
}
function Down(ele){
    var curHeight = ele.height();
    var autoHeight = ele.css('height', 'auto').height();
    if (!ele.hasClass('down')){
      ele.height(curHeight).animate({height: autoHeight},600,function(){
        ele.addClass('down')
      });
    }else{
      ele.height(curHeight).animate({height: 0},600,function(){
        ele.removeClass('down')
      });
    }
  }
$("#rule").on("click", function () {
    Down($("#rulebox"));
});

$("#btns").on("click", function () {
    Down($("#rulebox3"));
});



