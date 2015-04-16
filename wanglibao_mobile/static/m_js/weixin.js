(function () {

    $('.wei_kehuduan>a').on('click', function () {
        $('.wei_kehuduan').hide();
    });

    $('input').focus(function () {
        $(this).attr('placeholder', ' ');
    })
    log();
    wei_password();
    registered();

})();
function log() {
    $('.judge').on('click', function () {
        if ($(".ipon").val() == "") {
            alert("手机号码不能为空！");
            return false;
        } else if (!$(".ipon").val().match(/^1[3|4|5|8|9][0-9]\d{4,8}$/)) {
            alert("手机号码格式不正确！");
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
function wei_password() {
    $('#wei_buttonn').on('click', function () {
        if ($(".wei_word").val() == "") {
            alert("密码不能为空！");
            return false;
        } else if (!$(".wei_word").val().match(/^[0-9_a-zA-Z]{6,20}$/)) {
            alert("手机号码格式不正确！");
            return false;
        } else {
            var userName = $.trim($(".wei_word").val());

            wei_zheng();
            $.ajax({
                type: "POST",
                url: "/api/api-token-auth/",
                data: {identifier: pon, password: userName},
                dataType: "json",
                success: function (result) {
                    console.log(result);
                    console.log(result['token']);
                    var number_a = result['token'];
                    if (number_a !== '') {
                        window.location.href = "/mobile/weixin_app/";
                    } else {

                    }
                }
            })
        }

    })
}
function registered(pon) {
    $('#btn').click(function () {
        $('#btn').html('<span id="timeb2">60</span>秒后重新获取');
        timer = self.setInterval(addsec, 1000);
        wei_zheng()
        $.ajax({
            type: "POST",
            url: "/api/phone_validation_code/register/" + Verification() + "/",
            data: {},
            dataType: "json",
            success: function (result) {
                console.log(result);
                console.log(result['token']);
                var number_a = result['token'];
                if (number_a !== '') {
                    window.location.href = "/mobile/weixin_app/";
                } else {

                }
            }
        })
    });
    $('#wei_button').on('click', function () {
        var pass = $(".wei_pass").val(),
            qupass = $(".wei_quepass").val();

        if (pass == "") {
            alert("密码不能为空！");
            return false;
        } else if (!pass.match(/^[0-9_a-zA-Z]{6,20}$/)) {
            alert("手机号码格式不正确！");
            return false;
        } else if (pass === qupass) {

        } else {
            var userName = $.trim($(".wei_word").val());
            var url = window.location.search;


            // wei_zheng();
            $.ajax({
                type: "POST",
                url: "/api/accounts/register/ajax/",
                data: {identifier: pon, validate_code: userName, password: pp, invitecode: pp},
                dataType: "json",
                success: function (result) {
                    console.log(result);
                    console.log(result['token']);
                    var number_a = result['token'];
                    if (number_a !== '') {
                        window.location.href = "/mobile/weixin_app/";
                    } else {

                    }
                }
            })
        }

    })
}


functiongit {

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

function addsec() {

    var t = $('#timeb2').html();
    //alert(t);
    if (t > 0) {

        $('#timeb2').html(t - 1);
        //alert(t);
    } else {

        window.clearInterval(timer);
        $('#btn').html('<span id="timeb2"></span>重新获取验证码');
        //$('#btn').click(function(){getVerify();});
    }


}
function wei_zheng() {
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
}



