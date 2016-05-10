require.config({
    paths: {
        'jquery.modal': 'lib/jquery.modal.min',
        'activityRegister': 'activityRegister'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
});

require(['jquery', 'activityRegister'], function ($, re) {
    var count = 0;
    //注册
    re.activityRegister.activityRegisterInit({
        registerTitle :'领取迅雷会员+现金红包',    //注册框标语
        isNOShow : '1',
        activityUrl: '/activity/xunlei/'
    });

    $('#rewardDetail').on('click',function(){
        $('.explain-min').slideToggle("slow");
    })

     //滚动
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
        $('#winList').css({'top':-i+'px'})
      }
    }
    //挖宝
    $('.people-icon').on('click',function(){
        if($('#userStatus').val() == 'False'){
            $('body,html').animate({scrollTop: 0}, 600);
        }else{
            var self = $(this);
            if(count == 0){
                count = 1;
                setTimeout(function(){
                    self.addClass('people-icon2');
                    setTimeout(function(){
                        self.addClass('people-icon3');
                        count = 0;
                        setTimeout(function() {
                            $('.alert-box').modal({
                                modalClass: 'alert-box-c',
                                closeClass: 'close-btn'
                            })
                        },200)
                    },500)
                },300)
            }
        }
    })

    $('.userAction').on('click',function(){
        if($('#userStatus').val() == 'False'){
            $('body,html').animate({scrollTop: 0}, 600);
        }
    })
})