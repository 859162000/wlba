(function () {
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });

    require(['jquery', '/static/test/jwplayer.js'], function ($, jwplayer) {
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

        _getQueryStringByName = function (name) {
            var result = location.search.match(new RegExp('[\?\&]' + name + '=([^\&]+)', 'i'));
            if (result == null || result.length < 1) {
                return '';
            }
            return result[1];
        }
        //返回投票button
        $('.damaifu').on('click', function () {
            $('body,html').animate({scrollTop: 1257}, 600);
            return false
        });
        //请求票数接口
        $('.damai-buttonold').click(function () {
            redpack();
        })

        function redpack() {
            $.ajax({
                url: '/api/rock/finance/old_user/',
                type: "POST",
                data: {}
            }).done(function (damai) {
                if (damai['ret_code'] == 0) {
                    $('.tishiyu').text('恭喜！您已获得网利宝摇滚之夜门票');
                } else if (damai['ret_code'] == 1006) {
                    $('.tishiyu').text('您已领过网利宝摇滚之夜门票');
                } else if (damai['ret_code'] == 1005) {
                    $('.tishiyu').text('很抱歉，门票已经发完了');
                } else if (damai['ret_code'] == 1004) {
                    $('.tishiyu').text('很抱歉，没有在预定的时间内购标');
                } else if (damai['ret_code'] == 1003) {
                    $('.tishiyu').text('很抱歉，门票已经发完了');
                } else if (damai['ret_code'] == 1001) {
                    $('.tishiyu').text('很抱歉，您不满足领取资格，投资后再来领取吧亲');
                }


            });
        };
        var u = navigator.userAgent;
        function flashChecker() {
            var hasFlash = 0;
            var flashVersion = 0;
            if (document.all) {
                var swf = new ActiveXObject('ShockwaveFlash.ShockwaveFlash');
                if (swf) {
                    hasFlash = 1;
                    VSwf = swf.GetVariable("$version");
                    flashVersion = parseInt(VSwf.split(" ")[1].split(",")[0]);
                }
            } else {
                if (navigator.plugins && navigator.plugins.length > 0) {
                    var swf = navigator.plugins["Shockwave Flash"];
                    if (swf) {
                        hasFlash = 1;
                        var words = swf.description.split(" ");
                        for (var i = 0; i < words.length; ++i) {
                            if (isNaN(parseInt(words[i]))) continue;
                            flashVersion = parseInt(words[i]);
                        }
                    }
                }
            }
            return {
                f: hasFlash,
                v: flashVersion
            };
        }

        function IsPC() {
            var userAgentInfo = navigator.userAgent;
            var Agents = ["Android", "iPhone",
                "SymbianOS", "Windows Phone",
                "iPad", "iPod"];
            var flag = true;
            for (var v = 0; v < Agents.length; v++) {
                if (userAgentInfo.indexOf(Agents[v]) > 0) {
                    flag = false;
                    break;
                }
            }
            return flag;
        }

        window.jwplayer = $.extend(jwplayer, {'key': "F4UVreRdsAfmJwi9PjMJ8FXZOeG7ox0PN4l/Ig=="});
        if (navigator.userAgent.indexOf("Safari") > -1 && navigator.userAgent.indexOf("Chrome") == -1) {
            var str = '<video  autoplay webkit-playsinline controls id="video" src="http://pl.youku.com/playlist/m3u8?vid=347298192&type=mp4&ts=1453270222&keyframe=0&ep=dyaRGUuKVswC5yLXjD8bMX20ISUIXP0O8R2MidNrAtQmTeq7&sid=545327022218412fafeb7&token=2524&ctype=12&ev=1&oip=3550324874" >';
            $('#player').append(str);
        } else if (!IsPC()) {
            var str = '<video  autoplay webkit-playsinline controls id="video" src="http://pl.youku.com/playlist/m3u8?vid=347298192&type=mp4&ts=1453270222&keyframe=0&ep=dyaRGUuKVswC5yLXjD8bMX20ISUIXP0O8R2MidNrAtQmTeq7&sid=545327022218412fafeb7&token=2524&ctype=12&ev=1&oip=3550324874">';
            $('#player').append(str);
        } else {
            var fls = flashChecker();
            var s = "";
            if (!fls.f) alert("您没有安装flash,请下载flashplayer,并观看！");

            var w = $('#player').width();
            var h = w * 9 / 16;
            $('#player').height(h);
            var playerInstance = jwplayer('canver');
            playerInstance.setup({
                autostart: true,
                file: "http://pl.youku.com/playlist/m3u8?vid=347298192&type=mp4&ts=1453270222&keyframe=0&ep=dyaRGUuKVswC5yLXjD8bMX20ISUIXP0O8R2MidNrAtQmTeq7&sid=545327022218412fafeb7&token=2524&ctype=12&ev=1&oip=3550324874",
                width: '100%',
                height: '100%',
                primary: "flash",
                androidhls: true
            });
        }
    });
})();