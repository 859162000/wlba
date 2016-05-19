$(function() {
    window.onload = function() {
        $('.loading').hide();
        $('.no_signal_wrap').show().addClass('no_signal_wrap_animate');
        step1();
    }
    var choice_step1 = false;
    var choice_step2 = false;
    var choice_step3 = false;
    var money = 0;
    var this_money;

    var mp3 = document.getElementById("music"),play = $('#play');
    play.on('click', function (e) {
        if (mp3.paused) {
            mp3.play();
            $('#play').addClass('play_music').removeClass('close_music');
        } else {
            mp3.pause();
            $('#play').addClass('close_music').removeClass('play_music');
        }
    });

    /*数字变换*/
    function gold_scroll(gold_num_change) {
        $('.num-animate').each(function() {
            var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',');
            var key = parseInt($(this).attr('data-num'));
            $(this).prop('number',gold_num_change).animateNumber({
                number: key,
                numberStep: comma_separator_number_step
            },
            1000);
        })
    }
    /*数字变换*/

    function step1(){
        $('.boy_go').removeClass('boy_animate1');

        var i = 6;
        var timer1 = setInterval(function() {
            i--;
            if (i === 5){
                $('#wrap').css('opacity','1');
                $('.title').addClass('title_in');
            }
            if (i === 3){
                $('#play').show();
                mp3.play();
                $(document).one('touchstart', function () {
                    mp3.play();
                });
            }
            if (i === 0) {
                clearInterval(timer1);
                $('.no_signal_wrap').hide();
                $('.bat1').show().addClass('bat1_animate');
                step2();
            }
        },
        1000);
    }  

    function step2(){
        $('.money_50').show().addClass('money_50_animate');
        $('.gold_num_wrap').show().addClass('gold_num_wrap_animate');
        var i = 8;
        var timer1 = setInterval(function() {
            i--;
            if (i === 0) {
                clearInterval(timer1);
                gold_scroll(money);
                $('.gold_num_wrap .main').addClass('gold_num_main_animate');
                step3();
            }
        },
        1000);
    }   

    function step3(){
        var i = 4;
        var timer1 = setInterval(function() {
            i--;
            if (i === 0) {
                clearInterval(timer1);
                $('.boy_go').show().addClass('boy_animate1');
                //$('.boy_go_one').show();
                $('.choice_step1').show().addClass('choice_step_show');
                $('.bg_after').addClass('bg_after_animate1');
                $('.bg_front_wrap').addClass('bg_front_wrap_animate1');
                $('.boy_stay').hide();
                $('.gold').show().addClass('gold_animate');
                $('.cloud').addClass('cloud_animate1');
                choice_step1 = true;
            }
        },
        1000);
    }

    $('.choice_step1 .choice1').click(function(){
        if(choice_step1){
            choice_step1=false;
            $('.choice_step1').addClass('choice_step_hide');
            $('.gold_text').attr('data-num','70');
            $('.gold').addClass('gold_hide');
            //$('.boy_go_one').hide();
            $('.boy_stay').show();
            $('.boy_go').removeClass('boy_animate1');
            $('.gold_num_wrap .main').removeClass('gold_num_main_animate');
            money = 50;
            var i = 3;
            var timer1 = setInterval(function() {
                i--;
                if (i === 2) {
                    gold_scroll(money);
                    $('.gold_num_wrap .main').addClass('gold_num_main_animate');
                };
                if (i === 0) {
                    clearInterval(timer1);
                    $('.choice_step1').hide();
                    setp4();
                }
            },
            1000);
        }
    });


    $('.choice_step1 .choice2').click(function(){
        if(choice_step1){
            choice_step1 = false;
            $('.choice_step1').addClass('choice_step_hide');
            $('.gold').addClass('gold_hide2');
            $('.car').addClass('car_animate');
            //$('.boy_go_one').hide();
            $('.boy_stay').show();
            $('.boy_go').removeClass('boy_animate1');
            var i = 6;
            var timer1 = setInterval(function () {
                    i--;
                    if (i === 0) {
                        clearInterval(timer1);
                        $('.choice_step1').hide();
                        setp4();
                    }
                },
                1000);
        }
    });

    function setp4(){
        $('.boy_stay').hide();
        $('.boy_go_one').hide();
        $('.boy_go').show().addClass('boy_animate2');
        $('.cloud').addClass('cloud_animate2');
        $('.bg_after').addClass('bg_after_animate2');
        $('.bg_front_wrap').addClass('bg_front_wrap_animate2');
        $('.tree1_wrap').show().addClass('tree1_wrap_animate');
        $('.deadman').addClass('deadman_animate');
        $('.choice_step2').show().addClass('choice_step_show');
        var i = 6;
        var timer1 = setInterval(function() {
            i--;
            if (i === 0){
                clearInterval(timer1);
                $('.gold,.car,.choice_step1').hide();
                $('.boy_stay').show();     
                $('.ghost').show().addClass('ghost_animate');
                $('.boy_go').hide().removeClass('boy_animate2');
                choice_step2 = true;
            }
        },
        1000); 
    }

    $('.choice_step2 .choice1').click(function(){
        if(choice_step2) {
            choice_step2 = false;
            $('.boy_stay').hide();
            $('.boy_go').show().addClass('boy_animate4');
            $('.boy_run').show();
            $('.choice_step2').addClass('choice_step_hide');
            $('.cloud').addClass('cloud_animate4');
            $('.bg_after').addClass('bg_after_animate3');
            $('.bg_front_wrap').addClass('bg_front_wrap_animate3');
            $('.tree1_wrap').show().addClass('tree1_wrap_animate2');
            $('.gold_text').attr('data-num', '20');
            $('.tree2_wrap').show().addClass('tree2_wrap_animate');
            gold_scroll(money);
            $('.gold_num_wrap .main').addClass('gold_num_main_animate');
            var i = 6;
            var timer1 = setInterval(function () {
                    i--;
                    if (i === 3) {
                        $('.boy_run').hide();
                        $('.choice_step2').hide();
                    }
                    if (i === 0) {
                        clearInterval(timer1);
                        setp5();
                        $('.gold_num_wrap .main').removeClass('gold_num_main_animate');
                    }
                },
                1000);
            setp5();
        }
    });

    $('.choice_step2 .choice2').click(function(){
        if(choice_step2) {
            choice_step2 = false;
            $('.ghost_hit').show();
            $('.ghost').addClass('ghost_gone');
            $('.choice_step2').addClass('choice_step_hide');
            var i = 6;
            var timer1 = setInterval(function () {
                    i--;
                    if (i === 3) {
                        $('.choice_step2').hide();
                        $('.boy_stay').hide();
                        $('.boy_go').show().addClass('boy_animate3');
                        $('.cloud').addClass('cloud_animate3');
                        $('.bg_after').addClass('bg_after_animate4');
                        $('.bg_front_wrap').addClass('bg_front_wrap_animate4');
                        $('.tree1_wrap').show().addClass('tree1_wrap_animate2');
                        $('.tree2_wrap').show().addClass('tree2_wrap_animate2');
                        setp5();
                    }
                    ;
                    if (i === 0) {
                        clearInterval(timer1);
                        setp5();
                    }
                },
                1000);
        }
    });

    function setp5(){
        var i = 5;
        var timer1 = setInterval(function() {
            i--;
            if (i === 2){
                $('.choice_step3').show().addClass('choice_step_show');
            }
            if (i === 0){
                clearInterval(timer1);
                $('.boy_stay').show().css('opacity','1');
                $('.boy_go').hide();
                $('.girl_wrap').show().addClass('girl_come_animate');
                $('.girl_come').show();
                choice_step3 = true;
            }
        },
        1000);
        $('.sugar_want').addClass('sugar_want_animate');
    }

    $('.choice_step3 .choice1').click(function(){
        if(choice_step3) {
            choice_step3 = false;
            $('.sugar').show().addClass('sugar_animate');
            $('.choice_step3').addClass('choice_step_hide');
            $('.sugar_want').addClass('sugar_want_hide');
            this_money = $('.gold_text').attr('data-num') - 5;
            $('.gold_text').attr('data-num', this_money);
            money = $('.gold_text').text();
            var i = 6;
            var timer1 = setInterval(function () {
                    i--;
                    if (i === 4) {
                        $('.choice_step3').hide();
                        gold_scroll(money);
                        $('.gold_num_wrap .main').addClass('gold_num_main_animate');
                    }
                    if (i === 0) {
                        clearInterval(timer1);
                        step6();
                    }
                },
                1000);
        }
    });

    $('.choice_step3 .choice2').click(function(){
        if(choice_step3) {
            choice_step3 = false;
            $('.choice_step3').addClass('choice_step_hide');
            $('.girl_cry').show();
            $('.girl_come').css('opacity', '0');
            $('.sugar_want').addClass('sugar_want_hide');
            money = $('.gold_text').text();
            var i = 4;
            var timer1 = setInterval(function () {
                    i--;
                    if (i === 2){
                        $('.choice_step3').hide();
                    }
                    if (i === 0) {
                        clearInterval(timer1);
                        step6();
                    }
                },
                1000);
        }
    })

    function step6(){
        if(money<50){
            $('.poor_wrap').show();
            $('.poor_wrap .button').show().addClass('href_button');
            $('.poor_boy').show();
            $('.poor_text').addClass('text_animate');
        }else{
            $('.rich_wrap').show();
            $('.rich_wrap .button').show().addClass('href_button');
        }   $('.rich_text').addClass('text_animate');
    }

})
(function(){
    //微信分享
    var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ'];
    org.ajax({
        type : 'GET',
        url : '/weixin/api/jsapi_config/',
        dataType : 'json',
        success : function(data) {
            //请求成功，通过config注入配置信息,
            wx.config({
                debug: false,
                appId: data.appId,
                timestamp: data.timestamp,
                nonceStr: data.nonceStr,
                signature: data.signature,
                jsApiList: jsApiList
            });
        }
    });


    wx.ready(function(){

        var host = 'https://www.wanglibao.com/',
            shareName = '万圣夜出门的结果就是......',
            shareImg = host + '/static/imgs/mobile_activity/app_halloween/weixin.jpg',
            shareLink = host + '/activity/app_halloween/',
            shareMainTit = '万圣夜出门的结果就是......',
            shareBody = '没事别瞎溜达，除非......'
        //分享给微信好友
        org.onMenuShareAppMessage({
            title: shareMainTit,
            desc: shareBody,
            link: shareLink,
            imgUrl: shareImg
        });
        //分享给微信朋友圈
        org.onMenuShareTimeline({
            title: '万圣夜出门的结果就是......',
            link : shareLink,
            imgUrl: shareImg
        })
        //分享给QQ
        org.onMenuShareQQ({
            title: shareMainTit,
            desc: shareBody,
            link : shareLink,
            imgUrl: shareImg
        })
    })

})();