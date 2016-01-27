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
            $('.phone_code .status').hide();
            var phone = $('.phone_num').text();

            $('.get_code').attr('disabled', 'disabled').addClass('wait');
            time_count = 60;
            timerFunction();
            setInterval(timerFunction, 1000);

            $.ajax({
                url: '/api/phone_validation_code/' + phone + '/',
                type: 'POST',
                success: function (xhr) {

                    $('.phone_code .status').hide();

                },
                error: function (xhr) {
                    result = JSON.parse(xhr.responseText);
                    $('.phone_code .status .true').hide();
                    $('.phone_code .status .false').text(result.message).show();
                    $('.phone_code .status').show();

                    clearInterval(timerFunction);
                    time_count = 0;
                    $('.get_code').text('重新获取').removeAttr('disabled').removeClass('wait');
                }
            });
        });

        $('.button').click(function(){
            $('.error_form').hide();
            var validate_code_val = $('.input_code').val();
            var password_val = $('.password').val();
            var id_number_val = $('.id_number').val();
            var new_phone_val = $('.new_phone').val();
            var id_true,pass_true,post_data,card_no;

            if(id_number_val.length=='15'||id_number_val.length=='18'){
                $('.status_3').hide();
                id_true = true;
            }else{
                $('.status_3 .false').show().text('身份证位数错误').prev().hide();
                $('.status_3').show();
                id_true = false;
            }

            if(password_val.length<6){
                $('.status_2 .false').show().text('密码位数错误').prev().hide();
                $('.status_2').show();
                pass_true = false;
            }else{
                $('.status_2').hide();
                pass_true = true;
            }

            if(pass_true&&id_true){


                if($('input.bind_card').length>0){
                //当用户有同卡进出时
                    card_no = $('.bind_card').val();
                    post_data = {
                        'validate_code':validate_code_val,
                        'password':password_val,
                        'id_number':id_number_val,
                        'new_phone':new_phone_val,
                        'card_no':card_no
                    };
                }else {
                    post_data = {
                        'validate_code': validate_code_val,
                        'password': password_val,
                        'id_number': id_number_val,
                        'new_phone': new_phone_val
                    }
                }

                $.ajax({
                    url: '/api/sms_modify/vali_acc_info/' ,
                    type: 'POST',
                    data: post_data,
                    success: function (xhr) {

                        $('.error_form').hide();
                        $('.status .false').hide();
                        $('.status .true').show();
                        $('.status').show();
                        window.location.href = '/accounts/sms_modify/phone/';

                    },
                    error: function (xhr) {
                        result = JSON.parse(xhr.responseText);
                        $('.error_form').text(result.message).show();
                    }

                });
            }
        })

    })

}).call(this);