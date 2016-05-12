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

            //$.ajax({
            //    url: '/api/hmd_list/',
            //    type: 'get',
            //    success: function (data1) {
			//
            //        $('#product_name').text(data1.short_name);
            //        $('#display_status').text(data1.display_status);
			//
            //        $('#end_time_local').text('剩余：'+data1.end_time_local);
			//
			//
            //    },error: function(data1){
            //        $('.popup_box .text').text(data1.message);
            //        $('.popup_box .popup_button').hide();
            //        time_count = 3;
            //        time_intervalId = setInterval(timerFunction, 1000);
            //        time_intervalId;
            //    }
            //})


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