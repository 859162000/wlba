

$(function() {
    window.onload = function() {
        $('.no_signal_wrap').addClass('no_signal_wrap_animate');
        step1();
    }
    var choice_step1 = true;
    var choice_step2 = true;
    var choice_step3 = true;
    var money = 0;
    var this_money;
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

    function step1() {
        $('#wrap').css('opacity','1');
        $('.boy').removeClass('boy_animate1');
        var i = 4;
        var timer1 = setInterval(function() {
            i--;
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
        $('.title').addClass('title_animate');
        $('.money_50').show().addClass('money_50_animate');
        $('.gold_num_wrap').show().addClass('gold_num_wrap_animate');
        var i = 12;
        var timer1 = setInterval(function() {
            i--;
            if (i === 0) {
                clearInterval(timer1);
                $('.bat1,.title,.money_50').hide();
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
                //$('.boy_stay').show();
                $('.boy').addClass('boy_animate1');
                $('.choice_step1').show().addClass('choice_step_show');
                $('.bg_after').addClass('bg_after_animate1');
                $('.bg_front_wrap').addClass('bg_front_wrap_animate1');
                $('.boy_stay').hide();
                $('.gold').show().addClass('gold_animate');
                $('.cloud').addClass('cloud_animate1');
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
            $('.boy').removeClass('boy_animate1');
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
            $('.boy').removeClass('boy_animate1');
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
        $('.boy').addClass('boy_animate2');
        $('.cloud').addClass('cloud_animate2');
        $('.bg_after').addClass('bg_after_animate2');
        $('.bg_front_wrap').addClass('bg_front_wrap_animate2');
        $('.tree1_wrap').show().addClass('tree1_wrap_animate');
        $('.choice_step2').show().addClass('choice_step_show');
        var i = 6;
        var timer1 = setInterval(function() {
            i--;
            if (i === 0){
                clearInterval(timer1);
                $('.gold,.car,.choice_step1').hide();
                $('.boy_stay').show();     
                $('.ghost').show().addClass('ghost_animate');
                $('.boy').removeClass('boy_animate2');
            }
        },
        1000); 
    }

    $('.choice_step2 .choice1').click(function(){
        if(choice_step2) {
            choice_step2 = false;
            $('.boy_stay').css('opacity', '0');
            $('.boy_run').show();
            $('.choice_step2').addClass('choice_step_hide');
            $('.boy').addClass('boy_animate2');
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
                    if (i === 4) {
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
                        $('.boy').addClass('boy_animate3');
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
        var i = 6;
        var timer1 = setInterval(function() {
            i--;
            if (i === 2){
                $('.choice_step3').show().addClass('choice_step_show');
            }
            if (i === 0){
                clearInterval(timer1);
                $('.boy_stay').show().css('opacity','1');
                $('.girl_wrap').show().addClass('girl_come_animate');
                
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
        }else{
            $('.rich_wrap').show();
            $('.rich_wrap .button').show().addClass('href_button');
        }
    }

})