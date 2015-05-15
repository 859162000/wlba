
var org = (function(){
    var lib = {
        scriptName: 'mobile.js',
        _setShareData:function(ops,suFn,canFn){
            var setData = {};
            if(typeof ops == 'object'){
                for(var p in ops){
                    setData[p] = ops[p];
                }
            }
            typeof suFn =='function' && suFn != 'undefined' ? setData.success = suFn : "";
            typeof canFn =='function' && canFn != 'undefined' ? setData.cancel = canFn : "";
            return setData
        },
        _getQueryStringByName:function(name){
            var result = location.search.match(new RegExp("[\?\&]" + name+ "=([^\&]+)","i"));
             if(result == null || result.length < 1){
                 return "";
             }
             return result[1];
        },
        _getCookie :function(name){
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
        },
        _csrfSafeMethod :function(method){
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        },
        _sameOrigin:function(url){
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = "//" + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
        },
        /*
         * 分享到微信朋友
         */
        _onMenuShareAppMessage:function(ops,suFn,canFn){
            wx.onMenuShareAppMessage(lib._setShareData(ops,suFn,canFn));
        },
        /*
         * 分享到微信朋友圈
         */
        _onMenuShareTimeline:function(ops,suFn,canFn){
            wx.onMenuShareTimeline(wShare._setShareData(ops,suFn,canFn));
        }
    }
    return {
        scriptName : lib.scriptName,
        getQueryStringByName: lib._getQueryStringByName,
        getCookie : lib._getCookie,
        csrfSafeMethod : lib._csrfSafeMethod,
        sameOrigin : lib._sameOrigin,
        onMenuShareAppMessage : lib._onMenuShareAppMessage,
        onMenuShareTimeline : lib._onMenuShareTimeline
    }
})()


//login 没
var login = (function(org){
    var lib = {
        $captcha_img : $('#captcha'),
        $captcha_key : $('input[name=captcha_0]'),
        init:function(){
            lib._captcha_refresh()
            lib._checkFrom()
            lib._captcha_refresh_listen()
        },
        _captcha_refresh :function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function(res) {
                lib.$captcha_img.attr('src', res['image_url']);
                lib.$captcha_key.val(res['key']);
            });
        },
        _captcha_refresh_listen :function(){
            //刷新验证码
            lib.$captcha_img.on('click', function() {
                lib._captcha_refresh();
            });
        },
        _checkFrom:function(){
            var $form = $('#login-form');
            var $submit = $form.find('button[type=submit]');

            $('input[name=identifier], input[name=password], input[name=captcha_1]').on('focus', function() {
                var $self = $(this);
                var name = $self.attr('name').split('_')[0];
                $('.error-' + name).hide();
            });

            $submit.on('click', function() {
                var data = {
                    'identifier': $.trim($form.find('input[name=identifier]').val()),
                    'password': $.trim($form.find('input[name=password]').val()),
                    'captcha_0': $.trim($form.find('input[name=captcha_0]').val()),
                    'captcha_1': $.trim($form.find('input[name=captcha_1]').val()),
                    'openid': $.trim($form.find('input[name=openid]').val())
                }

                $.ajax({
                    'type': 'post',
                    'url': $form.attr('action'),
                    'data': data,
                    beforeSend: function (xhr, settings) {
                        $submit.attr('disabled', true);
                        if (!org.csrfSafeMethod(settings.type) && org.sameOrigin(settings.url)) {
                            xhr.setRequestHeader("X-CSRFToken", org.getCookie("csrftoken"));
                        }
                    },
                    success: function(res) {
                        alert('登录成功');
                        var next = org.getQueryStringByName('next');
                        if (next) {
                            window.location.href = next;
                        }
                        window.location.href = '/weixin/list/';
                    },
                    error: function(res) {
                        if (res['status'] == 403) {
                            alert('请勿重复提交');
                            return false;
                        }
                        var data = JSON.parse(res.responseText);
                        for (var key in data) {
                            key == '__all__' ? alert(data[key]) : $('.error-' + key).text(data[key]).show();
                        }
                    },
                    complete: function() {
                        $submit.removeAttr('disabled');
                    }
                });
                return false;
            });
        }
    }
    return {
        init : lib.init
    }


})(org)

var regist = (function(org){
    var lib ={
        init:function(){
            lib._checkFrom()
            lib._animateXieyi();
        },
        _animateXieyi:function(){
            var $submitBody = $(".submit-body"),
                $protocolDiv = $('.regist-protocol-div'),
                $cancelXiyi = $('.cancel-xiyie'),
                $showXiyi = $(".xieyi-btn"),
                $agreement = $("#agreement");
            //是否同意协议
            $agreement.change(function() {
              if ($(this).attr("checked") == 'checked') {
                $submitBody.addClass("disabled").attr('disabled', 'disabled');
                return $(this).removeAttr("checked");
              } else {
                $submitBody.removeClass("disabled").removeAttr('disabled');
                return $(this).attr("checked", "checked");
              }
            });
            //显示协议
            $showXiyi.on('click',function(event){
                event.preventDefault();
                $protocolDiv.css('top',"0");
            })
            //关闭协议
            $cancelXiyi.on('click',function(){
                $protocolDiv.css('top',"100%");
            })
        },
        _checkFrom:function(){
            //校验提示
            var signName = {'phone': ['phone-sign1', 'phone-sign2'], 'checkCode' : ['check-sign'], 'password': ['password-sign'], 'passwordRepeat': ['password-repeat-sign']}
            //校验方法
            var check ={
                phone:function(val, id){
                    $('#'+id).parents('.regist-list').find(".pub-check").hide();
                    var isRight = false;
                    var re = new RegExp(/^(13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
                    if(val){
                        re.test(val) ? isRight = true : ($('.'+signName[id][0]).show(),isRight = false);
                    }else{
                        $('#'+id).parents('.regist-list').find(".none-val").show();
                    }
                    return isRight;
                },
                checkCode:function(val){
                    return true
                },
                password:function(val, id){
                   if(6 > val.length || val.length > 20 ){
                       $('.'+signName[id][0]).show();
                       return false
                   }
                   return true
                },
                passwordRepeat:function(val, id){
                    if($('#password').val() != val){
                        $('.'+signName[id][0]).show();
                        return false
                    }
                    return true
                }
            }
            //验证码
            $('.request-check').on('click',function(){
                var phoneNumber = $("#phone").val(),
                    $that = $(this), //保存指针
                    count = 60,  //60秒倒计时
                    intervalId ; //定时器

                if(!check['phone'](phoneNumber, 'phone')) return //号码不符合退出
                $.ajax({
                    url: "/api/phone_validation_code/register/" + phoneNumber + "/",
                    type: "POST",
                    beforeSend: function(xhr, settings) {
                        //django配置post请求
                        if (!org.csrfSafeMethod(settings.type) && org.sameOrigin(settings.url)) {
                          xhr.setRequestHeader("X-CSRFToken", org.getCookie("csrftoken"));
                        }
                    },
                    error: function (xhr) {
                        clearInterval(intervalId);
                        $that.text('重新获取').removeAttr('disabled').removeClass('alreay-request');
                        var result = JSON.parse(xhr.responseText);
                        xhr.status === 429 ? alert('系统繁忙，请稍候重试') : alert(result.message);
                    }
                });

                $that.attr('disabled', 'disabled').addClass('alreay-request');
                //倒计时
                var timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return $that.text( count + '秒后可重发');
                    } else {
                        clearInterval(intervalId);
                        $that.text('重新获取').removeAttr('disabled').removeClass('alreay-request');
                        return
                    }
                };
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            });
            var isSubmit,
                dataList;
            //校验主函数
            $(".submit-body").on('click',function(){
                $('.pub-check').hide(),
                dataList = [], isSubmit =  true;
                $.each($('.input-public'), function(){
                    var value = $.trim($(this).val()), thisID = $(this).attr('id');
                    if(value){
                        check[thisID](value, thisID) ?  dataList.push(value) : isSubmit = false;
                    }else{
                        $(this).parents('.regist-list').find(".none-val").show();
                        isSubmit = false;
                    }
                })
            if(isSubmit){
                $.ajax({
                    url: "/api/register/",
                    type: "POST",
                    data: {'identifier': dataList[0], 'password': dataList[2], 'validate_code': dataList[1]},
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                          xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                        }
                    },
                    success:function(data){
                        console.log(data)
                    },
                    error: function (xhr) {

                    }
                });
            }
            })
        }
    }
    return {
        init : lib.init
    }
})(org)

//list
var list = (function(org){
    var lib = {
        windowHeight : $(window).height(),
        canGetPage : true, //防止多次请求
        scale : 0.7, //页面滚到百分70的时候请求
        pageSize: 10, //每次请求的个数
        page: 2, //从第二页开始
        init :function(){
            lib._scrollListen();
        },
        _scrollListen:function(){
            $(document).scroll(function(){
                if(document.body.scrollTop / (document.body.clientHeight -lib.windowHeight ) >= lib.scale){
                    lib.canGetPage && lib._getNextPage();
                }
            });
        },
        _getNextPage :function(){
            $.ajax({
                type: 'GET',
                url: '/api/p2ps/wx/',
                data: {page: lib.page, 'pagesize': lib.pageSize},
                beforeSend:function(){
                    lib.canGetPage =false
                },
                success: function(data){
                   $("#list-body").append(data.html_data);
                    lib.page++;
                    lib.canGetPage = true;
                },
                error: function(){
                    alert('Ajax error!')
                }
            })
        }

    };
    return {
        init : lib.init
    }
})(org)

var detail = (function(org){
    var lib ={
        weiURL: '/weixin/jsapi_config.json',
        countDown: $('#countDown'),
        init :function(){
            lib._tab();
            lib._animate();
            lib._share();
            lib.countDown.length > 0 && lib._countDown(lib.countDown)
        },
        _animate:function(){
            var $progress = $('.progress-percent');
            $(function(){
                setTimeout(function(){
                    var percent = parseFloat($progress.attr('data-percent'));
                    if(percent == 100){
                        $progress.css("margin-top","-10%");
                    }else{
                        $progress.css("margin-top", (100 - percent) + '%');

                    }
                    setTimeout(function(){
                        $progress.addClass('progress-bolang')
                    },1000)
                },300)
            })
        },
        _tab:function(){
            $(".toggleTab").on('click',function(){
                $(this).siblings().toggle();
                $(this).find('span').toggleClass('icon-rotate')
            })
        },
        _share: function(){
            var jsApiList = ["scanQRCode", "onMenuShareAppMessage","onMenuShareTimeline","onMenuShareQQ",];
            $.ajax({
                type : 'GET',
                url : lib.weiURL,
                dataType : "json",
                success : function(data) {
                    //请求成功，通过config注入配置信息,
                    wx.config({
                        debug: false,
                        appId: data.appId,
                        timestamp: data.timestamp,
                        nonceStr: data.nonceStr,
                        signature: data.signature,
                        jsApiList: jsApiList
                    });
                }
            });
            wx.ready(function(){
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: "haha",
                    desc: '没有什么啦',
                    link: "https://www.wanglibao.com",
                    imgUrl: "http://demo.open.weixin.qq.com/jssdk/images/p2166127561.jpg"},
                    function(){
                        alert("分享成功");
                    }
                );
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: "啦啦啦",
                    link : "https://www.wanglibao.com",
                    imgUrl: "http://demo.open.weixin.qq.com/jssdk/images/p2166127561.jpg"
                })
            })

        },
        _countDown:function(target){
            var endTimeList = target.attr("data-left").replace(/-/g,"/");
            var  TimeTo =function (dd){
                var t = new Date(dd),
                    n = parseInt(new Date().getTime()),
                    c = t - n;
                if( c <= 0 ){
                    target.text('活动已结束')
                    clearInterval(window['interval']);
                    return
                }
                var ds = 60*60*24*1000,
                    d = parseInt(c/ds),
                    h = parseInt((c-d*ds)/(3600*1000)),
                    m = parseInt((c - d*ds - h*3600*1000)/(60*1000)),
                    s = parseInt((c-d*ds-h*3600*1000-m*60*1000)/1000);
                    m < 10 ? m = "0" + m: '';
                    s < 10 ? s = "0" + s: '';
                    target.text(d+'天'+h+'小时'+m+'分'+s+'秒');
            }
            window['interval']= setInterval(function(){
                TimeTo(endTimeList);
            },1000);
        }
    }
    return {
        init : lib.init
    }
})(org)

~(function(org){
    $.each($("script"), function(index, item){
      var src = $(this).attr("src");
      if(src && src.indexOf(org.scriptName) > 0){
        if($(this).attr("data-init") && window[$(this).attr("data-init")]){
            window[$(this).attr("data-init")].init()
        }
      }
    })
})(org)
