$(function() {

    window.onload = function() {
        $('#wrap').show();
        $('.no_signal_wrap').addClass('no_signal_wrap_animate');
        step1();
    }    

    function step1() {
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
                gold_scroll();
                step3();
            }
        },
        1000);
        
    }   

    function step3(){
        $('.bg_after').delay(2000).animate({'backgroundPositionX': '15%'},4500);
        $('.bg_front_wrap').delay(2000).animate({'backgroundPositionX': '20%'},4500);
        $('.boy').addClass('boy_animate1');
        $('.boy_stay').hide();
        $('.gold').show().addClass('gold_animate');
        $('.choice_step1').show().addClass('choice_step_show');
    }


    /*数字变换*/
    function gold_scroll() {
        $('.num-animate').each(function() {
            var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',');
            var key = parseInt($(this).attr('data-num'));
            $(this).prop('number', 0).animateNumber({
                number: key,
                numberStep: comma_separator_number_step
            },
            1000);
        })
    }
    /*数字变换*/


    var step = 0;
    step0();
    function step0() {
        var i = 3;
        var timer1 = setInterval(function() {
            i--;
            if (i === 0) {
                clearInterval(timer1);
                //$('.girl_wrap').show();
                $('.bg_after_animate1').animate({'backgroundPositionX': '10%'},3000);
            }
        },
        1000);
    }

    function boy_animate() {

    }

    var j = 10;
    var timer2 = setInterval(function() {
        j--;
        if (j === 0) {
            clearInterval(timer2);
            step_wrap(step);
        }
    },
    1000);

    function step_wrap(step) {
        switch (step) {
        case 0:
            choice1();
            break;
        case 1:

            break;
        }
    }

    $('.choice .button').click(function(){
        $(this).addClass('choice_animate');
        $('.car').addClass('car_gone');
        $('.gold').addClass('gold_hide');
    });

    function choice1() {
        $('.choice').fadeIn(500);
        $('.choice1').click(function() {
            $('.choice').fadeOut(500);
            $('.boy').removeClass('boy_animate1').addClass('boy_animate2');
            
        });
    }

})
