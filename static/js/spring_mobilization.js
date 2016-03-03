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

        var time_count = 3;
        /*倒数秒数*/
        var time_intervalId;
        /*定义倒计时的名字*/

        var timerFunction = function () {
        /*定义倒计时内容*/
            if (time_count > 1) {
                time_count--;
                return $('.popup_box').show();
            } else {
                clearInterval(time_intervalId);
                /*清除倒计时*/
                $('.popup_box').hide();
                /*解锁按钮，可以点击*/
            }
        };

        /*翻牌*/
        var chance_num;
        var card_no;
        $('.card_box').click(function(){
            card_no=$(this).attr('data-card');

            if(h5_user_static){
                chance_num = $('#chance_num').text();
                if(chance_num>0){
                    if(!$(this).find('.card_box_main').hasClass('card_box_open')) {
                        chance_num--;
                        $('#chance_num').text(chance_num);
                        luck_draw();
                    }
                }else{
                    $('.popup_box .text').text('您还没有测试机会，赶紧去投资吧');
                    $('.popup_box').show();
                    time_count = 3;
                    time_intervalId = setInterval(timerFunction, 1000);
                    time_intervalId;
                }
            }else{
                window.location.href = '/accounts/login/?next=/weixin_activity/march_reward/'
            }

        });



        /*翻牌结束*/


        /*翻牌抽奖*/
        function luck_draw(){
            $.ajax({
                url: '/api/march_reward/fetch/',
                type: 'post',
                success: function (data1) {

                    $('.card_box[data-card="'+card_no+'"] .card_prize').text(data1.redpack.amount);
                    $(this).find('.card_box_main').addClass('card_box_open');

                },error: function(data1){
                    $('.popup_box .text').text(data1.message);
                    $('.popup_box').show();
                    time_count = 3;
                    time_intervalId = setInterval(timerFunction, 1000);
                    time_intervalId;
                }
            })
        }
        /*翻牌抽奖结束*/

        /*立即投资*/
        $('.button').click(function(){
            if(h5_user_static){
                window.location.href = '/p2p/list/'
            }else{
                window.location.href = '/accounts/login/?next=/p2p/list/'
            }
        })
        /*立即投资结束*/

    })

}).call(this);