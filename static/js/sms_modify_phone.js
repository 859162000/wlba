(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',

        },
        shim: {
            'jquery.modal': ['jquery'],
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

        /*输入手机号，验证码*/

        var time_count = 60;
        var timerFunction = function () {
            if (time_count >= 1) {
                time_count--;
                return $('.get_code').text(time_count + '秒后可重发');
            } else {
                clearInterval(timerFunction);
                $('.get_code').text('重新获取').removeAttr('disabled').removeClass('wait');
                //return $(document.body).trigger('from:captcha');
            }
        };

        $('.get_code').click(function(){
            $('.title_phone span.text_1').text('短信将发送至');
            $('.title_phone span.text_2').hide();
            $('.status_code').hide();
            var phone = $('.phone_num').text();
            $('.get_code').attr('disabled', 'disabled').addClass('wait');
            time_count = 60;
            timerFunction();
            setInterval(timerFunction, 1000);

            $.ajax({
                url: '/api/manual_modify/phone_validation_code/'+phone+'/',
                type: 'POST',
                success: function (xhr) {
                    $('.title_phone span.text_1').text('短信已经发送至');
                    $('.title_phone span.text_2').show();
                }
            });
        });

        $('.button').click(function(){
            var validate_code_val = $('.input_code').val();
            var phone = $('.phone_num').text();
            $.ajax({
                url: '/api/sms_modify/phone/'+phone+'/' ,
                type: 'POST',
                data: {
                    validate_code:validate_code_val,
                },
                success: function (returndata) {
                    window.location.href = '/accounts/security/';
                    alert(returndata);
                },
                error: function (returndata) {
                    alert(returndata);
                }

            });
        })

    })

}).call(this);