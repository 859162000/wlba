(function(){
    $('#lookMore').on('click',function(){
        var ele = $('.history-list');
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
    })
})();