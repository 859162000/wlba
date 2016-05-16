(function() {
    require.config({
        paths: {
            'jquery.modal': 'lib/jquery.modal.min',
            'activityRegister': 'activityRegister'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });
    require(['jquery', 'activityRegister'], function ($, re) {

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

      /*注册*/
      re.activityRegister.activityRegisterInit({
        registerTitle :'领取电影票＋现金红包',    //注册框标语
        isNOShow : '1',
        hasCallBack : true,
        callBack: function(){
            location.reload();

        }
      });
      /*注册结束*/


        $('.section_5_box p span').click(function(){
            var ele = $('.section_5_box .slide_text');

            if (!ele.hasClass('list_down')){
                $('.section_5_box .slide_text').slideDown('fast');
                ele.addClass('list_down');
                $('.section_5_box p span').addClass('open');
            }else{
                $('.section_5_box .slide_text').slideUp('fast');
                ele.removeClass('list_down');
                $('.section_5_box p span').removeClass('open');
            }
        })
    })



}).call(this);