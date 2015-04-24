(function () {


    $('.wei_kehuduan a').on('click', function () {
        $('.wei_kehuduan').hide();
    });

    $('#id').change(function () {
        if (document.getElementById("id").checked) {
            $('.weixin_tw').html('');

        } else {
            $('.weixin_tw').html('<span>注册需要同意网利宝用户协议</span>');
        }
    })


    log();
    wei_password();
    registered();
    retrieve();
    fee();
    yoa_registered()

})();

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

//$.ajaxSetup({
//    beforeSend: function (xhr, settings) {
//        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
//            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
//        }
//    }
//});

function log() {
    if (getQueryString('backurl') == '8888') {
        $('.top-i .jiao>img').on('click', function () {
            window.location.href = "/mobile/weixin_fee/";
        });
    } else {
        $('#weixin_fanhui_fa').hide();
    }
    //$('.top-i .jiao img').on('click', function () {
    //            window.location.href = "/mobile/weixin_fee/";
    //        });

    $('.judge').on('click', function () {
        if (getQueryString('backurl') == '8888') {
            sessionStorage.setItem("read", '8888');
        }
        if ($(".ipon").val() == "") {
            alert("手机号码不能为空！");
            return false;
        } else /*if(){

         }*/
        if (!$(".ipon").val().match(/^1[3|4|5|7|8|9][0-9]\d{8,8}$/)) {
            alert("请输入正确的手机号码");
            return false;
            //} else {
            //     var userName = $.trim($(".ipon").val());
            //    $.ajax({
            //        type: "get",
            //        url: "/api/user_exists/" + userName,
            //        data:{
            //
            //        },
            //        dataType: "json",
            //        success: function (result) {
            //            console.log(result['existing']);
            //            var number_a=result['existing'];
            //           if(number_a===true){
            //               window.location.href = "/mobile/weixin_inputt/";
            //           }else{
            //                window.location.href = "/mobile/weixin_registered/";
            //           }
            //        }
            //});
        }
    });
}
//=============================登入

function wei_password() {
    $('.top-i .jiao>.wei_fa').on('click', function () {
        window.location.href = "/mobile/weixin_index/?identifier=" + Verification();
    });
    $('#wx-mobel-btn,#box p,#box h1').on('click', function (e) {
        $('#wx-mobel-box').show()
        e.stopPropagation();
    })
    $('#wx-mobel-box,#off').on('click', function () {
        $('#wx-mobel-box').hide()
    })
    $('#wei_buttonn').on('click', function () {
        if ($(".wei_word").val() == "") {
            $('.weixin_ti').html('<span>密码不能为空！</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            });
            return false;
        } else if (!($(".wei_word").val().length >= 6 && $(".wei_word").val().length <= 20)) {
            $('.weixin_ti').html('<span>密码长度6-20位，请重新输入</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            });
            return false;
        } else {
            var userName = $.trim($(".wei_word").val());


            $.ajax({
                type: "POST",
                url: "/api/api-token-auth/",
                data: {identifier: Verification(), password: userName},
                dataType: "json",
                success: function (result) {
                    var number_a = result['token'];
                    if (number_a != 'false') {
                        alert('登录成功');
                        sessionStorage.setItem("name", Verification());
                        var read = sessionStorage.getItem("read");
                        if (read == '8888') {
                            window.location.href = "/mobile/weixin_fee/";
                        } else {
                            window.location.href = "/mobile/weixin_app/";
                        }
                    }
                    else {
                        alert('登录错误');
                    }
                },
                complete: function (XMLHttpRequest, textStatus) {
                    console.log(typeof XMLHttpRequest)
                    var $data = JSON.parse(XMLHttpRequest.responseText)
                    if ($data.non_field_errors) {

                        console.log($data.non_field_errors)
                        $('.weixin_ti').html('<span>账号密码不匹配，请重试。如果忘记密码，请点击找回密码</span>');
                        $('input').focus(function () {
                            $('.weixin_ti').html('');
                        });
                    }

                }
            })
        }

    })
}
//=============================注册
function registered() {
    $('.top-i .jiao>.wei_fann').on('click', function () {
        // window.location.href = "/mobile/weixin_index/";
        history.go(-1);
    });

    $('#btn').click(function () {
        if ($('#btn').attr('data-num') == 0) {
            var pno = Verification();

            $.ajax({
                type: "POST",
                url: "/api/weixin/phone_validation_code/register/" + pno + "/",
                success: function (result) {
                    if (result['message'] == '') {
                        $('#btn').attr('data-num', '1');
                        $('#btn').css('color', '#cccccc');
                        $('#btn').html('已发送<span id="timeb2" >60</span>秒');
                        timer = self.setInterval(addsec, 1000);
                        var time2 = setInterval(function () {
                            $('#btn').attr('data-num', '0');
                            $('#btn').css('color', '#2196f3');
                            clearInterval(time2)
                        }, 60000)
                    }
                    else {
                        alert(result['message'])
                    }
                },
                error: function (xhr) {
                    var data = JSON.parse(xhr.responseText);
                    alert(data['message']);
                }

            });

        }
    });


    $('#wei_button').on('click', function () {
        //$(".wei_pass").attr(maxlength)
        var pass = $(".wei_pass").val(),
            qupass = $(".wei_quepass").val(),
            yan = $(".wei_yan").val(),
            yao = $(".wei_yao").val();
        if (pass == "") {
            $('.weixin_ti').html('<span>信息不能为空，请填写完整</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            })
            return false;
        }
        if (!(pass.length >= 6 && pass.length <= 20)) {
            $('.weixin_ti').html('<span>密码长度6-20位，请重新输入</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            })
            return false;
        } else if (pass !== qupass) {
            $('.weixin_ti').html('<span>密码不一致，请重新输入</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            })
            return false;


        } else if (!document.getElementById("id").checked) {
            $('.weixin_tw').html('<span>注册需要同意网利宝用户协议</span>');

            return false
        } else if (pass == "" || qupass == "" || yan == "") {
            $('.weixin_tq').html('<span>信息不能为空，请填写完整</span>');
            $('input').focus(function () {
                $('.weixin_tq').html('');
            })

            return false;
        }

        $.ajax({
            type: "post",
            url: "/api/register/?promo_token=weixin",
            data: {identifier: Verification(), validate_code: yan, password: pass, invitecode: yao},
            dataType: "json",
            success: function (result) {

                if (result['ret_code'] == 0) {
                    alert('登录成功');
                    sessionStorage.setItem("name", Verification());
                    var read = sessionStorage.getItem("read");
                    if (read == '8888') {
                        window.location.href = "/mobile/weixin_fee/";
                    } else {
                        window.location.href = "/mobile/weixin_app/";
                    }
                }
                else if (result['ret_code'] == 30014) {
                    $('.weixin_tq').html('<span>' + result['message'] + '</span>');
                    $('input').focus(function () {
                        $('.weixin_tq').html('');
                    });
                }
                else {
                    alert(result['message']);
                }

            }
        })


    })

}

//=============================找回密码
function retrieve() {
    $('.top-i .jiao>.wei_fanh').on('click', function () {
        //window.location.href = "/mobile/weixin_inputt/";
        history.go(-1);
    });
    $('#btnn').click(function () {
        if ($('#btnn').attr('data-num') == 0) {
            $('#btnn').attr('data-num', '1');
            $('#btnn').css('color', '#cccccc');
            $('#btnn').html('已经发送<span id="timeb2">60</span>秒');
            timer = self.setInterval(addsecc, 1000);
            var pno = Verification();
            $.ajax({
                type: "POST",
                url: "/api/phone_validation_code/reset_password/" + pno + "/",
                success: function (result) {

                },
                complete: function (XMLHttpRequest, textStatus) {
                    if (typeof XMLHttpRequest == 'string') {
                        var $data = JSON.parse(XMLHttpRequest.responseText)
                        alert($data.message);
                    }

                }

            });
            var time2 = setInterval(function () {
                $('#btnn').attr('data-num', '0');
                $('#btnn').css('color', '#2196f3');
                clearInterval(time2)
            }, 60000)
        }

    });
    $('.wei_hui').on('click', function () {
        location.href = '/mobile/weixin_retrieve/?backurl=' + Verification();
    });
    $('#wei_but').on('click', function () {
        var pas = $(".wei_pas").val(),
            qupas = $(".wei_quepas").val(),
            ya = $(".wei_ya").val();
        if (pas == "") {
            $('.weixin_ti').html('<span>信息不能为空，请填写完整</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            });
            return false;
        }
        if (!(pas.length >= 6 && pas.length <= 20)) {
            $('.weixin_ti').html('<span>密码长度6-20位，请重新输入</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            });
            return false;
        } else if (pas !== qupas) {
            $('.weixin_ti').html('<span>密码不一致，请重新输入</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            });
            return false;


        } else if (pas == "" || qupas == "" || ya == "") {
            $('.weixin_tq').html('<span>信息不能为空，请填写完整</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            });
            return false;
        } else {

            var data = {new_password: pas, identifier: Verification(), validate_code: ya}
            $.ajax({
                type: "post",
                url: "/api/reset_password/",
                data: data,
                dataType: "json",
                success: function (result) {
                    if (result['ret_code'] == 0) {
                        alert(result['message']);
                        sessionStorage.setItem("name", data['identifier']);
                        window.location.href = "/mobile/weixin_inputt/?identifier=" + data['identifier'];
                        //history.go(-1);
                    }
                    else if (result['ret_code'] == 30004) {
                        $('.weixin_tq').html('<span>验证码错误</span>');
                        $('input').focus(function () {
                            $('.weixin_tq').html('');
                        });
                    }
                    else {
                        alert(result['message']);
                    }
                },
                complete: function (XMLHttpRequest, textStatus) {
                    //console.log(typeof XMLHttpRequest)
                    //var $dade = JSON.parse(XMLHttpRequest.responseText)
                    //console.log($dade);
                    //if ($dade.message == "验证码验证失败") {
                    //    $('.weixin_tq').html('<span>验证码错误</span>');
                    //    $('input').focus(function () {
                    //        $('.weixin_tq').html('');
                    //    });
                    //
                    //} else if ($dade.message.validate_code) {
                    //    alert($dade.message.validate_code);
                    //} else {
                    //     alert($dade.message);
                    //    sessionStorage.setItem("name", Verification());
                    //    //window.location.href = "/mobile/weixin_inputt/";
                    //     history.go(-1);
                    //
                    //}
                }
            })
        }

    })

}
//=============================邀请好友
function fee() {
    var name = sessionStorage.getItem("name");
    $('footer').hide();
    $('.wei_left').on('click', function () {
        window.location.href = "/mobile/weixin_index/?backurl=" + '8888';
    });
    $('.wei_right').on('click', function () {
        window.location.href = "/mobile/weixin_index/?backurl=" + '8888';
    });

    wx.config({
        debug: !!parseInt($('meta[name=debug]').attr('content')), // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
        appId: $('meta[name=app-id]').attr('content'), // 必填，公众号的唯一标识
        timestamp: $('meta[name=timestamp]').attr('content'), // 必填，生成签名的时间戳
        nonceStr: $('meta[name=noncestr]').attr('content'), // 必填，生成签名的随机串
        signature: $('meta[name=signature]').attr('content'),// 必填，签名，见附录1
        jsApiList: ['hideOptionMenu', 'showOptionMenu', 'onMenuShareTimeline', 'onMenuShareAppMessage', 'onMenuShareQQ'] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
    });

    wx.ready(function () {
        if (name == null) {
            $('footer').show();
            wx.hideOptionMenu();
        } else {
            wx.checkJsApi({
                'jsApiList': [
                    'onMenuShareTimeline'
                ]
            });
            var host = 'https://www.wanglibao.com';
            //var host = 'http://wanglibao.pythink.com';
            var share_link = host + '/mobile/weixin_feea/?identifier=' + name;
            var share_img_url = host + '/static/m_images/weixin_img/loginn.png';
            var share_title = '邀请好友来网利宝理财，首次体验双方各拿30元话费';
            wx.showOptionMenu();
            wx.onMenuShareTimeline({
                title: share_title, // 分享标题
                link: share_link, // 分享链接
                imgUrl: share_img_url
            });
            wx.onMenuShareAppMessage({
                title: '首次体验共享60元话费', // 分享标题
                desc: '邀请好友来网利宝理财，首次体验双方各拿30元话费', // 分享描述
                link: share_link, // 分享链接
                imgUrl: share_img_url, // 分享图标
                type: '', // 分享类型,music、video或link，不填默认为link
                dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
                success: function () {
                    // 用户确认分享后执行的回调函数
                },
                cancel: function () {
                    // 用户取消分享后执行的回调函数
                }
            });
            wx.onMenuShareQQ({
                title: '首次体验共享60元话费', // 分享标题
                desc: '邀请好友来网利宝理财，首次体验双方各拿30元话费', // 分享描述
                link: share_link, // 分享链接
                imgUrl: share_img_url, // 分享图标
                success: function () {
                    // 用户确认分享后执行的回调函数
                },
                cancel: function () {
                    // 用户取消分享后执行的回调函数
                }
            });
        }
    });

}

function feea() {

    var phon = $('input[name=identifier]').val(),
        wei_f = '',
        b = '';
    if (phon) {
        b = phon.substring(0, 3) + "****" + phon.substring(7, 11)
    }
    $('.wei_feea p label').html(b);
    $('#idd').change(function () {
        if (document.getElementById("idd").checked) {
            $('.wei_red').html('');

        } else {
            $('.wei_red').html('注册需要同意网利宝用户协议');

        }

    })


    $('.wei_ffee').click(function () {


        wei_f = $('.wei_fee').val();
        if (wei_f == "") {
            alert("手机号码不能为空！");
            return false;
        } else if (!$(".wei_fee").val().match(/^1[3|4|5|7|8|9][0-9]\d{8,8}$/)) {
            alert("请输入正确的手机号码");
            return false;
        } else if (!document.getElementById("idd").checked) {
            $('.wei_red').html('注册需要同意网利宝用户协议');
            return false
        } else {
            $.ajax({
                type: "POST",
                url: "/api/weixin/phone_validation_code/register/" + wei_f + "/",
                complete: function (XMLHttpRequest, textStatus) {
                    console.log(typeof XMLHttpRequest)
                    var $data = JSON.parse(XMLHttpRequest.responseText);
                    if ($data.message == '') {
                        alert('验证码已发送您的手机上请注意查收');
                        window.location.href = "/mobile/weixin_invitation/?identifier=" + wei_f + '&invite_code=' + phon;
                    } else {
                        alert($data.message);
                    }

                }

            });

        }

    });


}
function yoa_registered() {
    $('.top-i .jiao>.wei_fanhu').on('click', function () {
        // window.location.href = "/mobile/weixin_index/";
        history.go(-1);
    });
    if ($('.wei_xin').attr('data-num') == 0) {
        $('.wei_xin').attr('data-num', '1');
        $('.wei_xin').html('已发送<span id="timeb2">60</span>秒');
        timer = self.setInterval(addseca, 1000);

        var time2 = setInterval(function () {
            $('.wei_xin').attr('data-num', '0');
            $('.wei_xin').css('color', '#2196f3');
            clearInterval(time2)
        }, 60000)
    }

    $('.wei_xin').on('click', function () {
        if ($('.wei_xin').attr('data-num') == 0) {
            $('.wei_xin').attr('data-num', '1');
            $('.wei_xin').css('color', '#cccccc');
            $('.wei_xin').html('已发送<span id="timeb2">60</span>秒');
            timer = self.setInterval(addseca, 1000);
            var identifier = $('input[name=identifier]').val();
            $.ajax({
                type: "POST",
                url: "/api/weixin/phone_validation_code/register/" + identifier + "/",
                complete: function (XMLHttpRequest, textStatus) {
                    console.log(typeof XMLHttpRequest)
                    var $data = JSON.parse(XMLHttpRequest.responseText);
                    if ($data.message == '') {
                        //alert('验证码已发送您的手机上请注意查收');
                        //window.location.href = "/mobile/weixin_invitation/?identifier=" + wei_f + '&invite_code=' + phon;
                    } else {
                        alert($data.message);
                    }

                }

            });


            var time2 = setInterval(function () {
                $('.wei_xin').attr('data-num', '0');
                $('.wei_xin').css('color', '#2196f3');
                clearInterval(time2)
            }, 60000)

        }
    })
    var $btn = $('#wei_zhu');
    $btn.attr('disabled', false);
    $btn.on('click', function () {
        $btn.attr('disabled', true);

        var yanma = $(".yanma").val(),
            passwordd = $(".passwordd").val();
        if (yanma == "") {
            $('.weixin_ti').html('<span>信息不能为空，请填写完整</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            });
            $btn.attr('disabled', false);
            return false;
        }
        if (!(passwordd.length >= 6 && passwordd.length <= 20)) {
            $('.weixin_tq').html('<span>密码长度6-20位，请重新输入</span>');
            $('input').focus(function () {
                $('.weixin_tq').html('');
            })
            $btn.attr('disabled', false);
            return false;
        }
        if (yanma == "" || passwordd == "") {
            $('.weixin_ti').html('<span>信息不能为空，请填写完整</span>');
            $('input').focus(function () {
                $('.weixin_ti').html('');
            })
            $btn.attr('disabled', false);
            return false;
        } else {
            var data = {
                identifier: $('input[name=identifier]').val(),
                validate_code: yanma,
                password: passwordd,
                invite_code: $('input[name=invite_code]').val()
            }
            $.ajax({
                type: "post",
                url: "/api/register/?promo_token=weixin",
                data: data,
                dataType: "json",
                success: function (res) {
                    switch (res['ret_code']) {
                        case 0:
                            sessionStorage.setItem("name", data['identifier']);
                            window.location.href = "/mobile/weixin_app/";

                        default:
                            $('.weixin_tq').html('<span>' + res['message'] + '</span>');
                            $('input').focus(function () {
                                $('.weixin_tq').html('');
                            })
                    }
                },
                complete: function (XMLHttpRequest, textStatus) {
                    $btn.attr('disabled', false);
                    //console.log(typeof XMLHttpRequest)
                    //var $dade = JSON.parse(XMLHttpRequest.responseText)
                    //console.log($dade);
                    //if ($dade.message.identifier) {
                    //    alert($dade.message.identifier);
                    //} else if ($dade.message.validate_code) {
                    //    $('.weixin_tq').html('<span>' + $dade.message.validate_code + '</span>');
                    //    $('input').focus(function () {
                    //        $('.weixin_tq').html('');
                    //    })
                    //    //  alert($dade.message.validate_code);
                    //} else {
                    //    sessionStorage.setItem("name", Verification());
                    //    //window.location.href = "/mobile/weixin_app/";
                    //
                    //}
                }
            })
        }

    })
}
//=============================
function Verification() {

    var url = window.location.search;
    if (url.indexOf("?") != -1) {
        var str = url.substr(1)
        strs = str.split("&");
        for (i = 0; i < strs.length; i++) {
            var pon = strs[i].split("=")[1];
        }
    }
    return pon

}

function getQueryString(name) {
    var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
    var r = window.location.search.substr(1).match(reg);
    if (r != null) {
        return unescape(r[2]);
    }
    return null;
}


function addsec() {

    var t = $('#timeb2').html();
    //alert(t);
    if (t > 1) {

        $('#timeb2').html(t - 1);
        if (t) {

        }
    } else {

        window.clearInterval(timer);
        $('#btn').html('<span id="timeb2"></span>重新获取验证码');
        //$('#btn').click(function(){getVerify();});
    }


}
function addsecc() {

    var t = $('#timeb2').html();
    //alert(t);
    if (t > 1) {

        $('#timeb2').html(t - 1);
        //alert(t);
    } else {

        window.clearInterval(timer);
        $('#btnn').html('<span id="timeb2"></span>重新获取验证码');
    }
}
function addseca() {

    var t = $('#timeb2').html();
    if (t > 1) {

        $('#timeb2').html(t - 1);
    } else {

        window.clearInterval(timer);
        $('.wei_xin').html('<span id="timeb2"></span>重新获取验证码');


    }

}
function wei_yanzheng() {
    $('#wei_xieyi2').on('click', function () {
        history.go(-1);
    });
}




