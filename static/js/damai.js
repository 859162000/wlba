(function () {
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });

    require(['jquery'], function ($) {
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
            //判断点击选上在点击不选
            function setInp(self, id) {
                var inp = self.prev();
                if (inp.is(":checked")) {
                    inp.prop("checked", false);
                    self.removeAttr('id');
                } else {
                    inp.prop("checked", true);
                    self.attr('id', id);
                }
            }

            $('.labelone').click(function () {
                setInp($(this), "checked1");
            });
            $('.labelone1').click(function () {
                setInp($(this), "checked2");
            });
            $('.labelone2').click(function () {
                setInp($(this), "checked");
            });
            //点击投票传string给后台
            $('.toupiao').on('click', function () {
                    if ($(this).hasClass('toupiao')) {
                        var inp = $(".xuan-song1 input[type=radio]");
                        var chked = '';
                        var cur;
                        for (var i = 0; i < inp.length; i++) {
                            cur = inp.eq(i);
                            if (cur.is(":checked")) {
                                chked += cur.val() + ',';
                            }
                        }

                        var vaq = chked.substring(0, chked.length - 1);
                        if (vaq == '') {
                            $('.tishi').html('请至少选一个');
                        } else {
                            $.ajax({
                                url: '/api/rock/finance/',
                                type: "POST",
                                data: {'items': vaq}
                            }).done(function (data) {
                                redpack();
                                temer();
                                if (data['code'] == 0) {
                                    $('.ww').removeClass('toupiao');
                                    $('.tishi').html('投票成功');
                                    $('.ww').click(function () {
                                        $('.tishi').html('只能投一次');
                                    })
                                }
                                ;
                            })
                        }
                    }
                }
            )
            //投票截止日期
            function TimeTo(dd) {
                var t = new Date(dd),//取得指定时间的总毫秒数
                    n = new Date().getTime(),//取得当前毫秒数
                    c = t - n;//得到时间差
                if (c <= 0) {//如果差小于等于0  也就是过期或者正好过期，则推出程序
                    $('.tishi').html('已到投票截止日期');

                    $('.ww').removeClass('toupiao');

                    clearInterval(window['ttt']);//清除计时器
                    return;//结束执行
                }
            }

            temer()
            function temer() {
                window['ttt'] = setInterval(function () {
                    TimeTo('2016/1/6 00:00:00');//定义倒计时的结束时间，注意格式
                }, 1000);//定义计时器，每隔1000毫秒 也就是1秒 计算并更新 div的显示
            }
            //请求票数接口
            redpack();
            function redpack() {
                $.ajax({
                    url: '/api/rock/finance/?type=static',
                    type: "GET",
                    data: {}
                }).done(function (damai) {
                    var htm = $('.one');
                    var vaw = '';
                    for (var i in damai['records']) {
                        vaw += damai['records'][i] + ",";
                    }
                    ;
                    var vae = vaw.substring(0, vaw.length - 1);
                    var ss = vae.split(",");//string变数组用逗号分割
                    var max = Math.max.apply(null, ss);//取数组最大值
                    $.each(htm, function (i, o) {
                        var paio = $(o).text();
                        var paioshu = damai['records']
                        for (var i in paioshu) {

                            if (i == paio) {
                                if (paioshu[i] < 10) {
                                    paioshu[i] = "0" + paioshu[i];

                                }
                                $(o).parent().find('span').html(paioshu[i]);
                                $(o).parent().find('.xuan-tiao1').html('<div class=tiao style="width:' + (paioshu[i]) / max * 100 + '% "></div>');
                            }
                        }
                    })
                })
            }
        }
    )
    ;

})();