(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'underscore': 'lib/underscore-min',
            'Swiper':'lib/swiper_new_min'
        },
        shim: {
            'jquery.modal': ['jquery']

        }
    });
    require(['jquery','lib/countdown','Swiper'], function($, countdown) {

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

        function car_house_loan(){
            $.ajax({
                url: '/api/activity/chefangdai/',
                type: 'post',
                success: function (data) {
                    if(data.ret_code=='1002') {
                        $('.luck_title_wrap dl dt').text(data.message);
                        no_choujiang();
                        ranking_list(data.rewards_list);
                    }
                    if(data.ret_code=='1000') {
                        no_denglu();
                        ranking_list(data.rewards_list);
                    }
                    if(data.ret_code=='1001') {
                        $('.luck_title_wrap dl dt').text(data.message);
                        $('.luck_title_wrap dl dd').hide();
                        no_denglu();
                    }
                    if(data.ret_code=='0') {
                        $('.luck_title_wrap dl dt').text(data.message);
                        choujiang(data.content,data.result_no);
                    }

                }
            })
        }
        car_house_loan();

        function no_choujiang(){
            $('.popup_wrap dl dt').text('您暂时还没有抽奖机会哦~');
            $('.popup_wrap dl dd').text('马上投资指定产品，获得更多抽奖机会！！');
            $('.popup_wrap dl').show();
            $('.popup_text').hide();
            $('.popup_button').text('马上去');
            $('.popup_button').click(function(){
                window.location.href = '/p2p/list/'
            });
            $('.choujiang').click(function(){
                $('.popup_wrap').show();
            })
        }

        function no_denglu(){
            $('.popup_text').hide();
            $('.popup_wrap dl dt').text('您还未登陆！');
            $('.popup_wrap dl dd').text('请登录后查看抽奖机会！');
            $('.popup_wrap dl').show();
            $('.popup_button').text('马上去');
            $('.popup_button').click(function(){
                window.location.href = '/accounts/login/?next=/activity/chefangdai/'
            });
            $('.choujiang').click(function(){
                $('.popup_wrap').show();
            })
        }


        var this_time;
        function ranking_list(json){

            if(json.luck_list.length>0){
                var rankingList = [];
                var json_one;
                if(json.luck_list.length>7){
                    for(var i=0; i<7; i++){
                        json_one = json.luck_list[i];

                        this_time = json_one.time;
                        if(this_time>='86400'){
                            this_time = parseInt(this_time/86400)+'天'
                        }else if(this_time>='3600'){
                            this_time = parseInt(this_time/3600)+'小时'
                        }else if(this_time>='60'){
                            this_time = parseInt(this_time/60)+'分'
                        }else{
                            this_time = parseInt(this_time)+'秒'
                        }

                        rankingList.push(['<li><span class="one">'+json_one.phone.substring(0,3)+'****' +json_one.phone.substr(json_one.phone.length-4) +'</span><span class="two">'+json_one.name+'</span><span class="three">'+this_time+'前</span>'].join(''));

                    }
                }else{
                    for(var i=0; i<json.luck_list.length; i++){
                        json_one = json.luck_list[i];

                        this_time = json_one.time;
                        if(this_time>='86400'){
                            this_time = parseInt(this_time/86400)+'天'
                        }else if(this_time>='3600'){
                            this_time = parseInt(this_time/3600)+'小时'
                        }else if(this_time>='60'){
                            this_time = parseInt(this_time/60)+'分'
                        }else{
                            this_time = parseInt(this_time)+'秒'
                        }

                        rankingList.push(['<li><span class="one">'+json_one.phone.substring(0,3)+'****' +json_one.phone.substr(json_one.phone.length-4) +'</span><span class="two">'+json_one.name+'</span><span class="three">'+this_time+'前</span>'].join(''));

                    }
                }

                $('.ranking_list').html(rankingList.join(''));
                $('.ranking').show();
            }else{

                $('.no_ranking').show();
            }
        }

        function choujiang(data_text,result_no){
            var speed = 100;//速度
            var time = "";//创建一个定时器
              $(function () {
                $(".choujiang").click(function() {//触发事件
                  $("#msgBox").fadeOut();
                  doIt(1,1)//直接传入初始化参数，防止再次点击位置不对
                });
              });
              function doIt(t,i){//执行循环主方法
                time = setInterval(function () {
                  i++;
                  if (i > 8) {i = 1;t++;}
                  $(".cj").removeClass("cur");
                  $("#cj"+i).addClass("cur");
                  getLb(t,i);
                }, speed);
              }
              function getLb(t,i){//中奖之后的处理
                //console.log(t);
                //console.log(i);
                if (t == 3) {
                  if (i == result_no) {//此处的i为设定的中奖位置，也可用ajax去请求获得
                    clearInterval(time);
                    $('.popup_wrap dl').hide();
                    $('.popup_text').text(data_text).show();
                    $('.popup_button').text('继续抽奖');
                    $('.popup_button').click(function(){
                        car_house_loan();
                        $('.popup_wrap ').hide();

                    });
                  }
                }
              }
        }

        $('.popup_box .close_ico').click(function(){
            $('.popup_wrap ').hide();
        })

    })

}).call(this);