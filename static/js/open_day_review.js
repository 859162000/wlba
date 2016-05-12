(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'underscore': 'lib/underscore-min'
        },
        shim: {
            'jquery.modal': ['jquery']

        }
    });
    require(['jquery', 'lib/countdown'], function($, countdown) {

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

            $('.advantage_wrap .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.section_box4 .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.section_box5 .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.section_box6 .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.section_box7 .box').hover(function(){
                $(this).addClass('box_hover').siblings().removeClass('box_hover');
            })

            $('.body_wrap .slide_phone .small_box .img').click(function(){
                var data_src = $(this).attr('data-src');
                $(this).addClass('choose').siblings().removeClass('choose');
                $(this).parent().parent().find('.big_photo_img').attr('src',data_src);
            });

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

            $.ajax({
                url: '/api/activity/hmd_invest_ranks/',
                type: 'get',
                success: function (json) {
                    var rankingList = [];
                    var json_one;
                    for(var i=0; i<json.hmd_ranks.length; i++) {
                        json_one = json.hmd_ranks[i];
                        if (json_one != '') {
                            var number = fmoney(json_one.amount__sum, 0);
                            if (i < 3) {
                                if (i == 0) {
                                    rankingList.push(['<li class="first">'].join(''));
                                } else if (i == 1) {
                                    rankingList.push(['<li class="second">'].join(''));
                                } else if (i == 2) {
                                    rankingList.push(['<li class="third">'].join(''));
                                }
                                rankingList.push(['<span class="phone">' + json_one.phone.substring(0, 3) + '****' + json_one.phone.substr(json_one.phone.length - 4) + '</span><span class="num">'+number+'</span">'].join(''));

                            } else {
                                var i_num = i + 1;
                                rankingList.push(['<li><span class="phone">' + json_one.phone.substring(0, 3) + '****' + json_one.phone.substr(json_one.phone.length - 4) + '</span><span class="num">'+number+'</span"></li>'].join(''));
                            }
                        }
                    }
                    $('.ranking_list ul').html(rankingList.join(''));
                },error: function(data1){

                }
            })


            var fetchCookie, setCookie;
            $('.container').on('click', '.panel-p2p-product', function() {
              var url;
              url = $('.panel-title-bar a', $(this)).attr('href');
              return window.location.href = url;
            });
            $('.p2pinfo-list-box').on('mouseenter', function(e) {
              var target;
              target = e.currentTarget.lastChild.id || e.currentTarget.lastElementChild.id;
              return $('#' + target).show();
            }).on('mouseleave', function(e) {
              var target;
              target = e.currentTarget.lastChild.id || e.currentTarget.lastElementChild.id;
              return $('#' + target).hide();
            }).on('click', function() {
              var url;
              url = $('.p2pinfo-title-content>a', $(this)).attr('href');
              return window.location.href = url;
            });
            fetchCookie = function(name) {
              var arr, reg;
              reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
              if (arr = document.cookie.match(reg)) {
                return unescape(arr[2]);
              } else {
                return null;
              }
            };
            setCookie = function(key, value, day) {
              var date;
              date = new Date();
              date.setTime(date.getTime() + day * 24 * 60 * 60 * 1000);
              document.cookie = key + "=" + value + ";expires=" + date.toGMTString();
              return console.log(document.cookie);
            };
            $('.p2p-body-close').on('click', function() {
              $('.p2p-mask-warp').hide();
              return setCookie('p2p_mask', 'show', 15);
            });
            return (function(canShow) {
              if (!canShow) {
                return $('.p2p-mask-warp').show();
              }
            })(fetchCookie('p2p_mask'));
        })

}).call(this);