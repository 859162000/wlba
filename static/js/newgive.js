(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'activityRegister': 'activityRegister'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
  });

  require(['jquery','activityRegister'], function($,re) {
    //注册
    re.activityRegister.activityRegisterInit({
        registerTitle :'领取迅雷会员+现金红包',    //注册框标语
        isNOShow : '0',
        buttonFont: '立即注册'
    });
    var Rbtn= $("#btn_right"), Lbtn= $("#btn_left"),
        fabox= $("#fal_box").children(),
        len=fabox.length-1, index= 0, Millisecond=3000;
    fabox.first().css('opacity',1);
    Rbtn.on("click",function(){
      index++;
      if(index>len) index = 0;
      Focusmap();
    });
    Lbtn.on('click',function(){
      index--;
      if(index<0) index = len;
      Focusmap();
    });
    fabox.on("mouseover",function(){
      clearInterval(time)
    }).on("mouseout",function(){
      clearInterval(time)
      time = setInterval(timersFn, Millisecond);
    })
    timersFn = function(){
      index++;
      if(index>len) index = 0;
      fabox.eq(index).fadeIn().siblings().fadeOut();
    };
    Focusmap = function(){
      fabox.eq(index).fadeIn().siblings().fadeOut();
    };
    var time = setInterval(timersFn, Millisecond);

  });
}).call(this);
