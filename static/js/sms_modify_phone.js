(function() {
    require.config({
        paths: {
            jquery: '/static/js/lib/jquery.min',
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
        var result;
        $('.get_code').click(function(){
            $('.status_code').hide();
            $('.title_phone span.text_1').text('短信将发送至');
            $('.title_phone span.text_2').hide();
            var phone = $('.phone_num').text();
            $('.get_code').attr('disabled', 'disabled').addClass('wait');
            time_count = 60;
            timerFunction();
            setInterval(timerFunction, 1000);

            $.ajax({
                url: '/api/manual_modify/phone_validation_code/'+phone+'/',
                type: 'POST',
                success: function (xhr) {
                    if(xhr.status==200){
                        $('.status_code').hide();
                        $('.title_phone span.text_1').text('短信已经发送至');
                        $('.title_phone span.text_2').show();
                    }else{
                        clearInterval(timerFunction);
                        time_count = 0;
                        $('.get_code').text('重新获取').removeAttr('disabled').removeClass('wait');
                    }
                },
                error: function (xhr) {
                    result = JSON.parse(xhr.responseText);
                    $('.status_code .true').hide();
                    $('.status_code .false').text(result.message).show();
                    $('.status_code').show();

                    clearInterval(timerFunction);
                    time_count = 0;
                    $('.get_code').text('重新获取').removeAttr('disabled').removeClass('wait');
                }
            });

        });

        $('.button').click(function(){
            $('.error_form').hide();
            var validate_code_val = $('.input_code').val();
            var phone = $('.phone_num').text();
            $.ajax({
                url: '/api/sms_modify/phone/',
                type: 'POST',
                data: {
                    new_phone: phone,
                    validate_code:validate_code_val
                },
                success: function (xhr) {

                    if(xhr.status==200){
                        $('.error_form').hide();
                        $('.status_code .true').show();
                        $('.status_code .false').hide();
                        $('.status_code').show();
                        window.location.href = '/accounts/security/';
                    }else{
                        result = JSON.parse(xhr.responseText);
                        $('.error_form').text(result.message).show();
                    }
                },
                error: function (xhr) {
                    result = JSON.parse(xhr.responseText);
                    $('.error_form').text(result.message).show();
                }

            });
        })

    })

}).call(this);