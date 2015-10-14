(function(){
    $.extend($.fn, {
        scrollTo: function(m){
            var n = 0, timer = null, that = this;
            var smoothScroll = function(m){
                var per = Math.round(m / 50);
                n = n + per;
                if(n > m){
                    window.clearInterval(timer);
                    return false;
                }
                that.scrollTop(n);
            };

            timer = window.setInterval(function(){
                smoothScroll(m);
            }, 20);
        }
   })
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
    $(".ruleF").on("touchend", function () {
        Down($(".ruleC"));
    });

    $(".ruleF2").on("touchend", function () {
        Down($(".ruleC2"));
    });

     $('#page1').on('click',function(){
        var top = $('#page1Pos').offset().top;
        $('body,html').scrollTo(top);
     })

})();


