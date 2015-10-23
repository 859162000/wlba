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
        registerTitle :'领取520新用户红包',    //注册框标语
        isNOShow : '1',
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


    var $num = $('.gv_tzh')
    $num.each(function( ) {
      var amount = parseInt($(this).attr('data-number')).toString(),
          type = $(this).attr('data-type');
      $(this).append(amountGe(amount, type));
    })
    function amountGe(value, type){
      var len = value.length, str = '';
     // reType = type == 'man' ? '人' : '元';
      if(type == "amount"){
        if(len > 8){
          str = isNode(value.substr(0,len-8), '亿') + isNode(value.substr(len-8,4), '万') + isNode(value.substr(len-4,len), '元') ;
        }else{
          str = isNode(value.substr(0,len-4), '万') + isNode(value.substr(len-4,len), '元');
        }
      }else{
        str = isNode(value.substr(0,len), '位小伙伴');
      }

      function isNode(substr, text){
        if(parseInt(substr) > 0){
          return " <span class='num-animate'>" + parseInt(substr) + "</span> <span class='num-text'>" + text + '</span>';
        }
        return '';
      }
    return str
  }
  var login=$("#xun_login");
  login.on("click",function(){
    $(this).attr("href","/accounts/login/?next=/activity/baidu_finance/")
  })

  });
}).call(this);
