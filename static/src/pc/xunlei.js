require.config({
    paths: {
        'jquery.modal': 'lib/jquery.modal.min',
        'activityRegister': 'activityRegister',
        'csrf' : 'model/csrf'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
});

require(['jquery', 'activityRegister', 'csrf'], function ($, re) {
    var count = 0;
    //注册
    re.activityRegister.activityRegisterInit({
        registerTitle :'领取迅雷会员+现金红包',    //注册框标语
        isNOShow : '1',
        activityUrl: '/activity/xunlei_treasure/',
        hasCallBack: true,
        callBack: function () {
            if ($('#ret_code').val() == '10000') {
                window.location.href = "http://act.vip.xunlei.com/vip/cooplogin/?coop=wanglibao";
            }else {
                history.go(0);
            }
        }
    });
    //显示新用户奖励
    $('#rewardDetail').on('click',function(){
        $('.explain-min').slideToggle("slow");
    })
    //中奖用户列表
    winList();

    //可挖宝次数
    $.ajax({
        url: '/api/xunlei/treasure/',
        dataType: 'json',
        type: 'GET',
        data: {
            type: 'chances'
        },
        success: function (data) {
            $('#lotteryCounts').text(data.lefts);
        }
    })
    //挖宝
    $('.people-icon').on('click',function(){
        if($('#userStatus').val() == 'False'){
            $('body,html').animate({scrollTop: 0}, 600);
        }else{
            var self = $(this);
            if(count == 0) {
                count = 1;
                $.ajax({
                    url: '/api/xunlei/treasure/',
                    dataType: 'json',
                    type: 'post',
                    data: {},
                    success: function (data) {
                        if (data.code == 1002) {
                            $('#lotteryCounts').text(0);
                            $('.alert-box').modal({
                                modalClass: 'alert-box-c',
                                closeClass: 'close-btn',
                                showClose: false
                            })
                            $('#noChance').show();
                        } else if (data.code == 0) {
                            $('#lotteryCounts').text(data.lefts);
                            setTimeout(function () {
                                self.addClass('people-icon2');
                                setTimeout(function () {
                                    self.addClass('people-icon3');
                                    setTimeout(function () {
                                        $('.alert-box').modal({
                                            modalClass: 'alert-box-c',
                                            closeClass: 'close-btn',
                                            showClose: false
                                        })
                                        self.removeClass('people-icon2 people-icon3');
                                        if (data.type == '加息券') {
                                            $('#jxq').show();
                                            $('#jxq').find('span').text(data.amount);
                                        } else {
                                            $('#tyj').show();
                                            $('#tyj').find('span').text(data.amount);
                                        }
                                        winList();
                                        clearInterval(timer);
                                    }, 200)
                                }, 500)
                            }, 300)
                        } else if (data.code == 1) {
                            $('#lotteryCounts').text(data.lefts);
                            $('.alert-box').modal({
                                modalClass: 'alert-box-c',
                                closeClass: 'close-btn',
                                showClose: false
                            })
                            var array = ['no1', 'no2', 'no3'],
                                random = parseInt(3 * Math.random());
                            $('#' + array[random]).show();
                        }
                    }
                })
            }
        }
    })
    //关闭弹框
    $('.close-alert-box,.close-modal').on('click',function(){
        $.modal.close();$('.alert-c').hide(); count = 0;
    })
    //未注册用户操作效果
    $('.userAction').on('click',function(){
        if($('#userStatus').val() == 'False'){
            $('body,html').animate({scrollTop: 0}, 600);
        }
    })
    function winList() {
        $.ajax({
            url: '/api/xunlei/treasure/',
            dataType: 'json',
            type: 'GET',
            data: {
                type: 'orders'
            },
            success: function (data) {
                if (data.data == '') {
                    $('.win-box').hide()
                } else {
                    $('.win-box').show()
                    var str = '';
                    $.each(data.data, function (i, o) {
                        if (o.awards > 2) {
                            var strs = '<span>' + o.awards + '元</span>  体验金'
                        } else {
                            var strs = '<span>' + o.awards + '%</span>  加息券'
                        }
                        str += '<li>恭喜 ' + o.phone + ' 用户，获得 ' + strs + '</li>'
                    })
                    $('#winList').append(str);
                    if(data.data.length > 2){
                        scroll();
                    }
                }
            }
        })
    }
    //滚动
    var timer;
    function scroll(){
        var i= 1;
        clearInterval(timer);
        timer=setInterval(function(){
            if (-parseInt($('#winList').css('top'))>=$('#winList li').height()){
                $('#winList li').eq(0).appendTo($('#winList'));
                $('#winList').css({'top':'0px'})
                i=0
              }else{
                i++
                $('#winList').css({'top':-i+'px'})
            }
        },30)
    }
})