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


    function registered_success(){
        alert('1');
    }

    $('#button').click(function(){
        $('.register_wrap').show();
    })


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

			})
		}
	})

  });
}).call(this);