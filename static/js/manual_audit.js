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

        $('.button').click(function(){
            var id_number_val = $('#id_number').val();
            var validate_code_val = $('#validate_code').val();
            var password_val = $('#password').val();
            var pass_true = false;
            var id_true = false;

            if(id_number_val.length=='15'||id_number_val.length=='18'){
                $('.status_2').hide();
                id_true = true;
            }else{
                $('.status_2 .false').text('身份证位数错误');
                $('.status_2').show();
                id_true = false;
            }

            if(password_val.length<6){
                $('.status_1 .false').text('密码位数错误');
                $('.status_1').show();
                pass_true = false;
            }else{
                $('.status_1').hide();
                pass_true = true;
            }

            if(pass_true&&id_true){
                $.ajax({
                    url: '/api/manual_modify/vali_acc_info/' ,
                    type: 'POST',
                    data: {
                        id_number:id_number_val,
                        //validate_code:validate_code_val,
                        password:password_val
                    },
                    success: function (returndata) {
                        window.location.href = '/accounts/manual_modify/phone/';
                        alert(returndata);
                    },
                    error: function (returndata) {
                        alert(returndata);
                    }
                });
            }

        })

    })

}).call(this);