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

        $('#see_rule_1').on('click',function(){
            var ele = $('.rule_wrap_1');
            var curHeight = ele.height();
            var autoHeight = ele.css('height', 'auto').height();
            if (!ele.hasClass('down')){
                ele.height(curHeight).animate({height: autoHeight},500,function(){
                    ele.addClass('down');
                });
            }else{
                ele.height(curHeight).animate({height: 0},500,function(){
                    ele.removeClass('down');
                });
            }
        })
        $('#see_rule_2').on('click',function(){
            var ele = $('.rule_wrap_2');
            var curHeight = ele.height();
            var autoHeight = ele.css('height', 'auto').height();
            if (!ele.hasClass('down')){
                ele.height(curHeight).animate({height: autoHeight},500,function(){
                    ele.addClass('down');
                });
            }else{
                ele.height(curHeight).animate({height: 0},500,function(){
                    ele.removeClass('down');
                });
            }
        })
		$('#go_experience').click(function(){
            if(h5_user_static){
                window.location.href = '/activity/experience/gold/'
            }else{
                window.location.href = '/accounts/login/?next=/activity/experience/gold/'
            }

		});
    })

}).call(this);