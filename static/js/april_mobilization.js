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
                if(h5_user_static){
                    $('span#zero').hide();
                    $('span#chance_num').css('display','inline-block');
                }else{
                    $('span#chance_num').hide();
                    $('span#zero').css('display','inline-block');

                }
            }
        })

        function fmoney(s, type) {
            if (/[^0-9\.]/.test(s))
                return "0";
            if (s == null || s == "")
                return "0";
            s = s.toString().replace(/^(\d*)$/, "$1.");
            s = (s + "00").replace(/(\d*\.\d\d)\d*/, "$1");
            s = s.replace(".", ",");
            var re = /(\d)(\d{3},)/;
            while (re.test(s))
                s = s.replace(re, "$1,$2");
            s = s.replace(/,(\d\d)$/, ".$1");
            if (type == 0) {// 不带小数位(默认是有小数位)
                var a = s.split(".");
                if (a[1] == "00") {
                    s = a[0];
                }
            }
            return s;
        }



        function ajax_data(){
            $.ajax({
                url: '/api/april_reward/fetch/',
                type: 'post',
                success: function (json) {
                    substring(json.week_sum_amount);


                    var rankingList = [];
                    var json_one;
                    for(var i=1; i<json.weekranks.length; i++){
                        json_one = json.weekranks[i];
                        if(json_one!=''){
                            var number = fmoney(json_one.amount__sum, 0);
                            if(i<=3){
                                if(i==1){
                                    rankingList.push(['<tr class="first">'].join(''));
                                }else if(i==2){
                                    rankingList.push(['<tr class="second">'].join(''));
                                }else if(i==3){
                                    rankingList.push(['<tr class="third">'].join(''));
                                }
                                rankingList.push(['<td class="one"><span class="ico"></span><span class="phone">'+json_one.phone.substring(0,3)+'****' +json_one.phone.substr(json_one.phone.length-4) +'</span></td><td class="two">'+number+'元</td><td class="three">'].join(''));
                                if(i==1){
                                    rankingList.push(['5张百元加油卡+2张星美电影票</td></tr>'].join(''));
                                }else if(i==2){
                                    rankingList.push(['3张百元加油卡+2张星美电影票</td></tr>'].join(''));
                                }else if(i==3){
                                    rankingList.push(['2张百元加油卡+2张星美电影票</td></tr>'].join(''));
                                }
                            }else{
                                rankingList.push(['<tr><td class="one"><span class="ico">'+i+'</span><span class="phone">'+json_one.phone.substring(0,3)+'****' +json_one.phone.substr(json_one.phone.length-4) +'</span></td><td class="two">'+number+'元</td><td class="three">1张百元加油卡+2张星美电影票</td></tr>'].join(''));
                            }

                        }else{
                            rankingList.push(['<tr><td style="width:100%; text-align:center">虚位以待</td></tr>'].join(''));
                        }

                    }
                    $('.list_main tbody').html(rankingList.join(''));
                    substring_2(json.week_sum_amount);


                },error: function(data1){

                }
            })
        }
        /*翻牌抽奖结束*/
        ajax_data();

        /*逐个字符*/
        function substring(text){
            //alert(text.length);

            var num_length = text.length;
            if(num_length==13){
                num_length+=2;
            }
            if(num_length==14||num_length==10){
                num_length+=1;
            }

            for(var i=num_length; i>=0; i--) {
                if (num_length - 3 != i) {
                    //num = text.charAt(i);
                    if(num_length - 7 == i||num_length - 11 == i||num_length - 15 == i){
                        $('.num_wrap').prepend('<span class="num_2"></span>');
                        //alert(i);
                    }else{
                        if(num_length - 2 == i){
                            $('.num_wrap').prepend('<span class="num_3"></span>');
                        }else{
                            $('.num_wrap').prepend('<span class="num_1"></span>');
                        }

                    }

                }
            }
            if(text.length>=7){
                $('.num_wrap').prepend('<span class="num_1"></span>');
                if(text.length!=13&&text.length>10){
                    $('.num_wrap').prepend('<span class="num_1"></span>');
                }
            }
        };

        function substring_2(text){
            var num_2;
            var box_num_2 = $('.num_wrap .num_1').length;
            var box_num_3 = $('.num_wrap .num_2').length;
            for(var i=text.length;i>=0;i--) {
                if (text.length - 3 != i) {
                    num_2 = text.charAt(i);
                    $('.num_wrap .num_1').eq(box_num_2).text(num_2);
                    box_num_2--;
                }
            }

            var width = 78*$('.num_wrap .num_1').length+25*$('.num_wrap .num_2').length;
            $('.num_wrap').css('margin-left','-'+width/2+'px')

        };
        /*逐个字符结束*/


    })

}).call(this);