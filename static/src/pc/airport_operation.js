(function(){
    require.config({
        paths: {
            jquery : 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            tools: 'lib/modal.tools'
        },
        shim: {
            'jquery.model': ["jquery"]
        }
    })
    require(['jquery'],function($,re){

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
            success: function(data1) {
                h5_user_static = data1.login;
            }
        });
        var login = false;


        $(".air_btns").on("click",function(){

            $.ajax({
                type: "post",
                url: "/api/activity/konggang/",
                dataType: 'json',
                success: function(data){
                    if(data.ret_code='1000'){
                        window.location.href = '/accounts/login/?next=/activity/airport_operation/'
                    }else if(data.ret_code='1002'){
                        $('.popup_box .main .text').text(''+data.message+'');
                        $('.popup_box').show();
                    }else if(data.ret_code='0'){
                        $('.popup_box .main .text').text(''+data.message+'');
                        $('.popup_box').show();
                    }else if(data.ret_code='1003'){
                        $('.popup_box .main .text').text(''+data.message+'');
                        $('.popup_box').show();
                    }

                    //console.log(data)
                }
            })


        })
        $('.popup_box .popup_button').click(function(){
            $('.popup_box').hide();
        });
    })



}).call(this);