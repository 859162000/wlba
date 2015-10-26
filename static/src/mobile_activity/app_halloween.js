

$(function() {

    window.onload = function() {
        $('#wrap').show();
        $('.no_signal_wrap').addClass('no_signal_wrap_animate');
        step1();
    }    

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
                gold_scroll(0);
                step3();
            }
        },
        1000);
        
    }   

    function step3(){
        $('.bg_after').addClass('bg_after_animate1');
        $('.bg_front_wrap').addClass('bg_front_wrap_animate1');
        $('.boy').addClass('boy_animate1');
        $('.boy_stay').hide();
        $('.gold').show().addClass('gold_animate');
        $('.choice_step1').show().addClass('choice_step_show');
    }

    $('.choice_step1 .choice1').click(function(){
        $('.choice_step1').addClass('choice_step_hide');
        $('.gold_text').attr('data-num','70');
        $('.gold').addClass('gold_hide');
        var i = 1;
        var timer1 = setInterval(function() {
            i--;
            if (i === 0) {
                clearInterval(timer1);
                gold_scroll(50);
            }
        },
        1000);
        
    });

    $('.choice_step1 .choice2').click(function(){
        $('.choice_step1').addClass('choice_step_hide');
        $('.gold').addClass('gold_hide2');
        $('.car').addClass('car_animate');
    });

})