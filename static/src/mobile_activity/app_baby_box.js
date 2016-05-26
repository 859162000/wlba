
(function(org) {

    $('#take_prize,#take_prize_2').click(function() {
        org.ajax({
            url: '/api/activity/xiaomei/',
            type: 'post',
            success: function (data) {
                if(data.ret_code=='1000'){
                    window.location.href = '/weixin/regist/?promo_token=xmdj2&next=/activity/app_pretty_reach_home/?promo_token=xmdj2'
                }else if(data.ret_code=='1001'||data.ret_code=='1002'){
                    $('.popup_box .main .textairport').text(''+data.message+'');
                    $('.popup_box').show();
                }else if(data.ret_code=='1002'||data.ret_code=='1004'){
                    $('.popup_box .main .textairport').text(''+data.message+'');
                    $('.popup_box').show();
                }else{
                    $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                    $('.popup_box').show();
                }
            }
        })
    })
    
})(org);
