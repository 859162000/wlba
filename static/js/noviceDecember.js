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

		var csrfSafeMethod, getCookie, sameOrigin,
          getCookie = function (name) {
              var cookie, cookieValue, cookies, i;
              cookieValue = null;
              if (document.cookie && document.cookie !== "") {
                  cookies = document.cookie.split(";");
                  i = 0;
                  while (i < cookies.length) {
                      cookie = $.trim(cookies[i]);
                      if (cookie.substring(0, name.length + 1) === (name + "=")) {
                          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                          break;
                      }
                      i++;
                  }
              }
              return cookieValue;
          };
      csrfSafeMethod = function (method) {
          return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
      };
      sameOrigin = function (url) {
          var host, origin, protocol, sr_origin;
          host = document.location.host;
          protocol = document.location.protocol;
          sr_origin = "//" + host;
          origin = protocol + sr_origin;
          return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
      };
      $.ajaxSetup({
          beforeSend: function (xhr, settings) {
              if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                  xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
              }
          }
      });

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
				window.location.href = '/activity/experience/gold/'
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