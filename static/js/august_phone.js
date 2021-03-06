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

        $('#show_button').on('click',function(){
            var ele = $('#show_list');

            if (!ele.hasClass('list_down')){
                $('#show_list').slideDown('fast');
                ele.addClass('list_down');
                $('#show_button').addClass('open');
            }else{
                $('#show_list').slideUp('fast');
                ele.removeClass('list_down');
                $('#show_button').removeClass('open');
            }
        })

        $('#button_link').click(function() {
            $.ajax({
                url: '/api/activity/zhaoxiangguan/',
                type: 'post',
                success: function (data) {
                    if(data.ret_code=='1000'){
                        window.location.href = '/accounts/login/?promo_token=sy&next=/activity/august_phone/?promo_token=sy'
                    }else if(data.ret_code=='1'||data.ret_code=='1001'||data.ret_code=='1002'){
                        $('.popup_box .main .textairport').text(''+data.message+'');
                        $('.popup_box').show();
                    }else if(data.ret_code=='0'){
                        if(data.tag=='标记成功'){
                            window.location.href = '/p2p/list/?promo_token=sy'
                        }else{
                            $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                            $('.popup_box').show();
                        }
                    }
                }
            })
        })
        $('.popup_box .popup_button').click(function(){
            $('.popup_box').hide();
        });

    })

}).call(this);