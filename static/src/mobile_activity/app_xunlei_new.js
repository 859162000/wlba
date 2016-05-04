org.ui = (function(){
    var lib = {
        _alert: function(txt, callback,btn){
            var alertFram = '';
            if(document.getElementById("alert-cont")){
                document.getElementById("alert-cont").innerHTML = '';
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
                alertFram = document.getElementById("alert-cont");
                shield = document.getElementById("popubMask");
            }else{
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText="position:fixed;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;height:100%";
                alertFram = document.createElement("DIV");
                alertFram.id="alert-cont";
            }
            //if(difference == 2){
            //    strHtml = "<div id='alertTxt' class='popub-txt investWin'><p><img src='/static/imgs/mobile_activity/app_experience/right.png'/></p>";
            //    strHtml+="<p class='successFonts'>恭喜您投资成功！</p><p>到期后体验金自动收回</p><p>收益自动发放</p></div>";
            //}else if(difference == 4){
            //    strHtml ="<div id='alertTxt' class='popub-txt oldUserWin'><p class='p_center'>"+ txt +"</p>";
            //    strHtml+="<p><img src='/static/imgs/mobile_activity/app_experience/logo.png'/></p><p class='popub-footer'><div class='close_btn'>知道了！</div></p></div>";
            //}
            strHtml = "<div class='xunlei-alert'>'"+ txt +"'<p class='popub-footer'><div class='close_btn close-alert'>"+ btn +"</div><div class='cha'></div></div>";
            alertFram.innerHTML = strHtml;
            document.body.appendChild(alertFram);
            document.body.appendChild(shield);

            $('.close_btn,.cha').on('click',function(){
                alertFram.style.display = "none";
                shield.style.display = "none";
                callback && callback();
            })
            document.body.onselectstart = function(){return false;};
        }
    }

    return {
        alert : lib._alert
    }
})();
;(function(org){
    var count = 0;
   $('#rewardDetail').on('click',function(){
        var ele = $('.explain-min');
        var curHeight = ele.height()
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

     //无线滚动
    var timer,i= 1,j=2;
    timer=setInterval(function(){
      scroll();
    },30)

    function scroll(){
      if (-parseInt($('#winList').css('top'))>=$('#winList li').height()){
        $('#winList li').eq(0).appendTo($('#winList'));
        $('#winList').css({'top':'0px'})
        i=0
      }else{
        i++
        $('#winList').css({'top':-i+'px'});
      }
    }

    $('.people-icon').on('click',function(){
        var self = $(this);
        if(count == 0){
            count = 1;
            setTimeout(function(){
                self.addClass('people-icon2');
                setTimeout(function(){
                    self.addClass('people-icon3');
                    count = 0;
                    org.ui.alert('<div class="two-line-sty"><p>人世间最美好的事情莫不过如此，</p><p>88元体验金已经在您的账户中！</p></div>', '', '太棒了')
                },500)
            },300)
        }
    })
})(org);