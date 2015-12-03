(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });
    require(['jquery'],
    function($, re) {

        var h5_user_static;
		$.ajax({
			url: '/api/user_login/',
			type: 'post',
			success: function (data1) {
				h5_user_static = data1.login;
			}
		})

		$('.take_red,#zhuce').click(function(){
			if(h5_user_static){
				$('.title_wrap').show();
			}else{
				window.location.href = '/activity/experience/gold/'
			}
		});

		$('.take_first_red').click(function(){
			if(h5_user_static){
				window.location.href = '/p2p/list/'
			}else{
				window.location.href = '/accounts/login/?next=/p2p/list/'
			}
		});

		$('.click_rule').click(function(){
            if($('.strategy_wrap').hasClass('strategy_wrap_show')) {
                $('.strategy_wrap').removeClass('strategy_wrap_show');
            }else{
                $('.strategy_wrap').addClass('strategy_wrap_show');
            }
		});
		$('.see_red_rule').click(function(){
            if($('.recommend_send_red').hasClass('recommend_send_red_show')) {
                $('.recommend_send_red').removeClass('recommend_send_red_show');
            }else{
                $('.recommend_send_red').addClass('recommend_send_red_show');
            }
		});
		$('.title_wrap .close,.title_wrap .button').click(function(){
			$('.title_wrap').hide();
		});
    })

}).call(this);