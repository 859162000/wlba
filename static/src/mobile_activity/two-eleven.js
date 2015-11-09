(function(){
    function Down(ele){
        var curHeight = ele.height();
        var autoHeight = ele.css('height', 'auto').height();
        if (!ele.hasClass('down')){
          ele.height(curHeight).animate({height: autoHeight},500,function(){
            ele.addClass('down')
          });
        }else{
          ele.height(curHeight).animate({height: 0},500,function(){
            ele.removeClass('down')
          });
        }
    }
    $(".dianji").on("click", function () {
        Down($(".app-eleven-guizhe"));
    });

    $("#jiaxi0 ").on("click", function () {
        Down($(".footer-guizhe"));
    });
    $(".app-bidjiaxi").on("click", function () {
        Down($(".app-bid-guizhe1"));
    });

     $('#page1').on('click',function(){
        var top = $('#page1Pos').offset().top;
        $('body,html').scrollTo(top);
     })

})();
