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

		$('.recharge_button').click(function(){
			window.location.href = '/p2p/list/'
		});

        $('.investment_button').click(function(){
		    window.location.href = '/p2p/list/'
		});

        var see_rule_button_index;
        $('.see_rule_button').click(function(){
            see_rule_button_index = $(this).parent().next().hasClass('rule_wrap_show');
            if(see_rule_button_index){
                $(this).parent().next().removeClass('rule_wrap_show').hide();
            }else{
                $(this).parent().next().addClass('rule_wrap_show').show();
            }
        });
    })

    //无线滚动
    var timer, i = 1, j = 2;
    timer = setInterval(function () {
        scroll();
    }, 30)

    function scroll() {
        if (-parseInt($('.list_scroll').css('top')) >= $('.list_scroll p').height()) {
            $('.list_scroll p').eq(0).appendTo($('.list_scroll'));
            $('.list_scroll').css({'top': '0px'})
            i = 0
        } else {
            i++;
            $('.list_scroll').css({'top': -i + 'px'})
        }
    }

	$('#reward_button').click(function(){
		$(this).addClass('select').next().removeClass('select');
		$('.take_reward_list').show().prev().hide();
	});
	$('#rule_button').click(function(){
		$(this).addClass('select').prev().removeClass('select');
		$('.rule_wrap').show().next().hide();
	});
}).call(this);