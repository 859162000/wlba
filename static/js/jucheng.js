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


  require(['jquery','activityRegister'], function($,re) {
    //注册
    re.activityRegister.activityRegisterInit({
        registerTitle :'限时限量，满额直送',    //注册框标语
        isNOShow : '1',
        hasCallBack : true,
        callBack : function(){
            alert('1')
        }

    });

    var has_ticket;
    //判断是否有买票
    var is_user;
    if($('#ganjiwang-welcome').index()!=0){
    //未登陆
        is_user = 0;
    }else{
        is_user = 1;
        $.ajax({
            url: '/api/gift/owner/?promo_token=jcw',
            type: "POST",
            data: {
                'action':'HAS_TICKET'
            }
        }).done(function (json) {
            has_ticket = json.has_ticket;
        });
    }


    function registered_success(){
        alert('1');
    }

    $('#button').click(function(){
        if(has_ticket){
            $('.register_wrap').show();
        }else{
            if(is_user == 0){
                $('.register_wrap').show();
            }else{
                $('.get_ticket').show();
            }
        }
    });

    $('#get_ticket_button').click(function(){
        $('.get_ticket').hide();
        $('.write_info').show();
    });


	$('.write_info').click(function(){
		var name = $('input.name').val();
		var phone = $('input.phone').val();
		var address = $('input.address').val();
		if(name&&phone&&address){
			$.ajax({
				url: '/api/gift/owner/?promo_token=jcw',
				type: "POST",
				data: {
					phone : name,
					address : phone,
					name : name
				}
			}).done(function (json) {
                $('.write_info .text').text(json.message);
			})
		}
	})

  });
}).call(this);