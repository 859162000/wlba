
(function(org) {

    $('#take_prize,#take_prize_2').click(function() {
        org.ajax({
            url: '/api/activity/baobeigezi/',
            type: 'post',
            success: function (data) {
                if(data.ret_code=='1000'){
                    window.location.href = '/weixin/regist/?promo_token=bg&next=/activity/app_baby_box/h5/?promo_token=bg'
                }else if(data.ret_code=='1002'){
                    window.location.href = '/weixin/list/?promo_token=bg'
                }else if(data.ret_code=='1001'||data.ret_code=='1002'||data.ret_code=='1004'){
                    $('.popup_box .main .textairport').text(''+data.message+'');
                    $('.popup_box').show();
                }else{
                    $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                    $('.popup_box').show();
                }
            }
        })
    })


    $('.popup_box .popup_button,.popup_box .close_popup').click(function(){
        $('.popup_box').hide();
    });
    $('.slideDown_button').on('click',function(){
        var ele = $('.slideDown_box');
        var curHeight = ele.height();
        var autoHeight = ele.css('height', 'auto').height();
        if (!ele.hasClass('down')){
            $('.slideDown_button').addClass('open');
            ele.height(curHeight).animate({height: autoHeight},500,function(){
                ele.addClass('down');

            });
        }else{
            $('.slideDown_button').removeClass('open');
            ele.height(curHeight).animate({height: 0},500,function(){
                ele.removeClass('down');

            });

        }
    });
})(org);
