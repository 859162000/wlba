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

            alert(password_val);
            alert(id_number_val);
            $.ajax({
                url: '/api/manual_modify/vali_acc_info/' ,
                type: 'POST',
                data: {
                    id_number:id_number_val,
                    //validate_code:validate_code_val,
                    password:password_val
                },
                success: function (returndata) {
                    alert(returndata);
                },
                error: function (returndata) {
                    alert(returndata);
                }
            });
        })

    })

}).call(this);