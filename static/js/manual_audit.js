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


        $('.button').click(function(){
            $('.error_form').hide();

            var id_number_val = $('#id_number').val();
            var password_val = $('#password').val();
            var pass_true = false;
            var id_true = false;

            if(id_number_val.length=='15'||id_number_val.length=='18'){
                $('.status_2').hide();
                id_true = true;
            }else{
                $('.status_2 .false').show().text('身份证信息有误').prev().hide();
                $('.status_2').show();
                id_true = false;
            }

            if(password_val.length<6){
                $('.status_1 .false').show().text('账户登录密码有误').prev().hide();
                $('.status_1').show();
                pass_true = false;
            }else{
                $('.status_1').hide();
                pass_true = true;
            }

            var card_no_true;
            if ($('input.bind_card').length > 0) {
				if ($('input.bind_card').val().length >= 10 && $('input.bind_card').val().length <= 20) {
					$('.status_3').hide();
					card_no_true = true;
				} else {
                    $('.status_3 .false').show().text('银行卡号码有误').prev().hide();
					$('.status_3').show();
					card_no_true = false;
				}
			}

            var card_no;
            var post_data;
            if($('input.bind_card').length>0){
            //当用户有同卡进出时
                card_no = $('.bind_card').val();
                post_data = {
                    'id_number':id_number_val,
                    'password':password_val,
                    'card_no':card_no
                };
                if(pass_true&&id_true&&card_no_true){
                    $.ajax({
                        url: '/api/manual_modify/vali_acc_info/' ,
                        type: 'POST',
                        data: post_data,
                        success: function (xhr) {
                            window.location.href = '/accounts/manual_modify/phone/';
                        },
                        error: function (xhr) {
                            result = JSON.parse(xhr.responseText);
                            $('.error_form').text(result.message).show();
                        }
                    });
                }
            }else {
                post_data = {
                    'id_number':id_number_val,
                    'password':password_val
                }
                if(pass_true&&id_true){
                    $.ajax({
                        url: '/api/manual_modify/vali_acc_info/' ,
                        type: 'POST',
                        data: post_data,
                        success: function (xhr) {
                            window.location.href = '/accounts/manual_modify/phone/';
                        },
                        error: function (xhr) {
                            result = JSON.parse(xhr.responseText);
                            $('.error_form').text(result.message).show();
                        }
                    });
                }
            }
        })

    })

}).call(this);