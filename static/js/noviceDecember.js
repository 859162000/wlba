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
    require(['jquery', 'activityRegister'],
    function($, re) {
        re.activityRegister.activityRegisterInit({
            registerTitle: '限时限量，满额直送',
            isNOShow: '1',
            hasCallBack: true,
            callBack: function() {
                $.ajax({
                    url: '/api/gift/owner/?promo_token=jcw',
                    type: "POST",
                    data: {
                        phone: '',
                        address: '',
                        name: '',
                        action: 'ENTER_WEB_PAGE'
                    }
                }).done(function(json) {

                })
            }
        })

		$('.take_red').click(function(){
			if($('#denglu').index()){
				$('.title_wrap').show();
			}else{
				window.location.href = '/activity/experience/gold/'
			}
		});

		$('.take_first_red').click(function(){
			if($('#denglu').index()){
				window.location.href = '/p2p/list/'
			}else{
				window.location.href = '/accounts/login/?next=/p2p/list/'
			}
		});

		$('.click_rule').click(function(){
			$('.strategy_wrap').addClass('strategy_wrap_show');
		});
		$('.see_red_rule').click(function(){
			$('.recommend_send_red').addClass('recommend_send_red_show');
		});
		$('.title_wrap .close,.title_wrap .button').click(function(){
			$('.title_wrap').hide();
		});
    })

}).call(this);