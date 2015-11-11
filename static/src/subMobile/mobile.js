var org = (function(){
    document.body.addEventListener('touchstart', function () { }); //ios 触发active渲染
    var lib = {
        scriptName: 'mobile.js',
        _ajax :function(options){
            $.ajax({
                url: options.url,
                type: options.type,
                data: options.data,
                dataType : options.dataType,
                beforeSend: function(xhr, settings) {
                    options.beforeSend && options.beforeSend(xhr);
                    //django配置post请求
                    if (!lib._csrfSafeMethod(settings.type) && lib._sameOrigin(settings.url)) {
                      xhr.setRequestHeader('X-CSRFToken', lib._getCookie('csrftoken'));
                    }
                },
                success:function(data){
                    options.success && options.success(data);
                },
                error: function (xhr) {
                    options.error && options.error(xhr);
                },
                complete:function(){
                    options.complete && options.complete();
                }
            });
        },
        _calculate :function(dom, callback){
            var calculate = function(amount, rate, period, pay_method) {
                var divisor, rate_pow, result, term_amount;
                if (/等额本息/ig.test(pay_method)) {
                    rate_pow = Math.pow(1 + rate, period);
                    divisor = rate_pow - 1;
                    term_amount = amount * (rate * rate_pow) / divisor;
                    result = term_amount * period - amount;
                } else if (/日计息/ig.test(pay_method)) {
                    result = amount * rate * period / 360;
                } else {
                    result = amount * rate * period / 12;
                }
                return Math.floor(result * 100) / 100;
            };

            dom.on('input', function() {
                _inputCallback();
            });

            function _inputCallback(){
                var earning, earning_element, earning_elements, fee_earning;
                var target = $('input[data-role=p2p-calculator]'),
                    existing = parseFloat(target.attr('data-existing')),
                    period = target.attr('data-period'),
                    rate = target.attr('data-rate')/100,
                    pay_method = target.attr('data-paymethod');
                    activity_rate = target.attr('activity-rate')/100;
                    activity_jiaxi = target.attr('activity-jiaxi')/100;
                    amount = parseFloat(target.val()) || 0;

                if (amount > target.attr('data-max')) {
                    amount = target.attr('data-max');
                    target.val(amount);
                }
                activity_rate += activity_jiaxi;
                amount = parseFloat(existing) + parseFloat(amount);
                earning = calculate(amount, rate, period, pay_method);
                fee_earning = calculate(amount, activity_rate, period, pay_method);

                if (earning < 0) {
                    earning = 0;
                }
                earning_elements = (target.attr('data-target')).split(',');

                for (var i = 0; i < earning_elements.length; i ++) {
                    earning_element = earning_elements[i];
                    if (earning) {
                        fee_earning = fee_earning ? fee_earning : 0;
                        earning += fee_earning;
                        $(earning_element).text(earning.toFixed(2));
                    } else {
                        $(earning_element).text("0.00");
                    }
                }
                callback && callback();
            }
        },
        _getQueryStringByName:function(name){
            var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
             if(result == null || result.length < 1){
                 return '';
             }
             return result[1];
        },
        _getCookie :function(name){
            var cookie, cookieValue, cookies, i;
                cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    cookies = document.cookie.split(';');
                    i = 0;
                    while (i < cookies.length) {
                      cookie = $.trim(cookies[i]);
                      if (cookie.substring(0, name.length + 1) === (name + '=')) {
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
            sr_origin = '//' + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
        },
        _setShareData:function(ops,suFn,canFn){
            var setData = {};
            if(typeof ops == 'object'){
                for(var p in ops){
                    setData[p] = ops[p];
                }
            }
            typeof suFn =='function' && suFn != 'undefined' ? setData.success = suFn : '';
            typeof canFn =='function' && canFn != 'undefined' ? setData.cancel = canFn : '';
            return setData
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
            wx.onMenuShareTimeline(lib._setShareData(ops,suFn,canFn));
        },
        _onMenuShareQQ:function(){
            wx.onMenuShareQQ(lib._setShareData(ops,suFn,canFn));
        }
    }
    return {
        scriptName             : lib.scriptName,
        ajax                   : lib._ajax,
        calculate              : lib._calculate,
        getQueryStringByName   : lib._getQueryStringByName,
        getCookie              : lib._getCookie,
        csrfSafeMethod         : lib._csrfSafeMethod,
        sameOrigin             : lib._sameOrigin,
        onMenuShareAppMessage  : lib._onMenuShareAppMessage,
        onMenuShareTimeline    : lib._onMenuShareTimeline,
        onMenuShareQQ          : lib._onMenuShareQQ,
    }
})();

org.ui = (function(){
    var lib = {
        _alert: function(txt, callback){
            if(document.getElementById("alert-cont")){
                document.getElementById("alertTxt").innerHTML = txt;
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
            }else{
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText="position:absolute;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
                var alertFram = document.createElement("DIV");
                alertFram.id="alert-cont";
                alertFram.style.cssText="position:absolute; top:35%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
                strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 1.25rem .75rem;'>"+txt+"</div>";
                strHtml += " <div class='popub-footer' style='width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;'>确认</div>";
                alertFram.innerHTML = strHtml;
                document.body.appendChild(alertFram);
                document.body.appendChild(shield);

                $('.popub-footer').on('click',function(){
                    alertFram.style.display = "none";
                    shield.style.display = "none";
                    callback && callback();
                })
            }
            document.body.onselectstart = function(){return false;};
        },
        _showSign:function(signTxt, callback){
            var $sign = $('.error-sign');
            if($sign.length == 0){
                $('body').append("<section class='error-sign'>" + signTxt + "</section>");
                $sign = $('.error-sign');
            }else{
                $sign.text(signTxt)
            }
            ~function animate(){
                $sign.css('display','block');
                setTimeout(function(){
                    $sign.css('opacity', 1);
                    setTimeout(function(){
                        $sign.css('opacity', 0);
                        setTimeout(function(){
                            $sign.hide();
                            return callback && callback();
                        },300)
                    },1000)
                },0)
            }()
        },
        /*
          .form-list
              .form-icon.user-phone(ui targer).identifier-icon（事件target）
              .form-input
                input(type="tel", name="identifier", placeholder="请输入手机号",data-target2='identifier-icon'（事件target）, data-icon='user-phone'(ui事件), data-target="identifier-edit"(右侧操作), data-empty=''（input val空的时候的classname）, data-val='input-clear'（input val不为空的时候的classname）).foreach-input
                .form-edit-icon.identifier-edit（右边操作如：清空密码）
         */
        _inputStyle:function(options){
            var $submit = options.submit,
                inputArrList = options.inputList;

            $.each(inputArrList, function(i){
                inputArrList[i]['target'].on('input',function(){
                    var $self = $(this);
                    if($self.val() == ''){
                        inputForClass([
                            { target: $self.attr('data-target'), addName : $self.attr('data-empty'), reMove : $self.attr('data-val')},
                            { target: $self.attr('data-target2'), addName : $self.attr('data-icon'), reMove : ($self.attr('data-icon')+"-active")},
                        ])
                        $submit.attr('disabled', true);
                    }else{
                        inputForClass([
                            { target: $self.attr('data-target'), addName : $self.attr('data-val'),reMove : $self.attr('data-empty')},
                            { target: $self.attr('data-target2'), addName : ($self.attr('data-icon')+"-active"), reMove : $self.attr('data-icon')}
                        ])
                    }
                    canSubmit() ? $submit.css('background','rgba(219,73,63,1)').removeAttr('disabled') : $submit.css('background','rgba(219,73,63,.5)').attr('disabled')
                })
            })

            //用户名一键清空
            $('.identifier-edit').on('click', function(e){
                $(this).siblings().val('').trigger('input');
            })
            //密码隐藏显示
            $('.password-handle').on('click',function(){
                if($(this).hasClass('hide-password')){
                    $(this).addClass('show-password').removeClass('hide-password');
                    $(this).siblings().attr('type','text');
                }else if($(this).hasClass('show-password')){
                    $(this).addClass('hide-password').removeClass('show-password');
                    $(this).siblings().attr('type','password');
                }
            })

            var inputForClass = function(ops){
                if(!typeof(ops) === 'object') return ;
                $.each(ops, function(i){
                    $('.'+ops[i].target).addClass(ops[i].addName).removeClass(ops[i].reMove);
                })
            }
            var returnCheckArr = function(){
                var returnArr = [];
                for(var i = 0; i < arguments.length; i++){
                    for(var arr in arguments[i]){
                        if(arguments[i][arr]['required'])
                          returnArr.push(arguments[i][arr]['target'])
                    }
                }
                return returnArr
            }
            var canSubmit = function(){
                var isPost = true, newArr = [];

                newArr = returnCheckArr(options.inputList, options.otherTarget);

                $.each(newArr, function(i, dom){
                    if(dom.attr('type') == 'checkbox'){
                        if (!dom.attr('checked'))
                            return  isPost =  false
                    }else if (dom.val() == '')
                        return  isPost =  false
                });

                return isPost
            }
        },
    }
    return {
        focusInput: lib._inputStyle,
        showSign : lib._showSign,
        alert : lib._alert,
    }
})();
org.detail = (function(org){
    var lib ={
        weiURL: '/weixin/api/jsapi_config/',
        init :function(){
            //lib._share(obj);
            lib._downPage();
        },
        /*
        * 微信分享
         */
        _share: function(obj){
            var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
            org.ajax({
                type : 'GET',
                url : lib.weiURL,
                dataType : 'json',
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
                var host = 'https://staging.wanglibao.com',
                    shareImg,//图片
                    shareLink,//连接地址
                    shareMainTit,//分享标题
                    shareBody,//分享描述
                    success;
                var conf = $.extend({
                    shareImg: host + '/static/imgs/sub_mobile/logo.png',//图片
                    shareLink: host + '/weixin/award_index/',//连接地址
                    shareMainTit: '幸运大转盘，日日有惊喜',//分享标题
                    shareBody: '转盘一动，大奖即送。还不快快领取！',//分享描述
                    success: function(){//成功事件
                    }
                }, obj || {});
                shareImg = conf.shareImg;
                shareLink = conf.shareLink;//连接地址
                shareMainTit = conf.shareMainTit;//分享标题
                shareBody = conf.shareBody;//分享描述
                success = conf.success;
                alert(shareMainTit);
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg,
                    success: function(){
                        alert(shareMainTit);
                    }
                });
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: shareMainTit,
                    link : shareLink,
                    imgUrl: shareImg,
                    success: function(){
                        alert(shareMainTit);
                    }
                });
                //分享给QQ
                org.onMenuShareQQ({
                    title: shareMainTit,
                    desc: shareBody,
                    link : shareLink,
                    imgUrl: shareImg
                });
            })
        },
        _downPage:function(){
          var u = navigator.userAgent,
              ua = navigator.userAgent.toLowerCase(),
              footer  =  document.getElementById('footer-down'),
              isAndroid = u.indexOf('Android') > -1 || u.indexOf('Linux') > -1,
              isiOS = !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
          $('#down-btn').on('click',function(){

            if (ua.match(/MicroMessenger/i) == "micromessenger") {
                window.location.href = 'http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao&g_f=991653';
            }else{
              if(isiOS){
                window.location.href = 'https://itunes.apple.com/cn/app/wang-li-bao/id881326898?mt=8';
              }else if(isAndroid) {
                window.location.href = 'https://www.wanglibao.com/static/wanglibao1.apk';
              }else{
                window.location.href = 'http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao&g_f=991653';
              }
            }
          })
        }
    }
    return {
        init : lib.init,
        share: lib._share
    }
})(org);
org.login = (function(org){
    var lib = {
        $captcha_img : $('#captcha'),
        $captcha_key : $('input[name=captcha_0]'),
        init:function(){
            //lib._captcha_refresh();
            lib._checkFrom();
        },
        _captcha_refresh :function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function(res) {
                lib.$captcha_img.attr('src', res['image_url']);
                lib.$captcha_key.val(res['key']);
            });
        },
        _checkFrom:function(){
            var $form = $('#login-form'),
                $submit = $form.find('button[type=submit]');
            org.ui.focusInput({
                submit : $('button[type=submit]'),
                inputList: [
                    {target : $('input[name=identifier]'),  required:true},
                    {target : $('input[name=password]'), required : true},
                ],
            });

            //刷新验证码
            //lib.$captcha_img.on('click', function() {
              //  lib._captcha_refresh();
            //});
            $submit.on('click', function() {
                var data = {
                    'identifier': $.trim($form.find('input[name=identifier]').val()),
                    'password': $.trim($form.find('input[name=password]').val()),
                    'openid': $.trim($form.find('input[name=openid]').val())
                };
                org.ajax({
                    'type': 'post',
                    'url': $form.attr('action'),
                    'data': data,
                    beforeSend: function (xhr) {
                        $submit.attr('disabled', true).text('登录中..');
                    },
                    success: function(res) {
                        org.ajax({
                           'type': 'post',
                            'url': '/weixin/api/bind/',
                            'data': {'openid': data.openid},
                            success: function(data){
                                window.location.href = "/weixin/jump_page/?message=" + data.message;
                            },
                            error: function(data){
                                window.location.href = "/weixin/jump_page/?message=" + data.message;
                            }
                        });
                    },
                    error: function(res) {
                        if (res['status'] == 403) {
                            org.ui.showSign('请勿重复提交');
                            return false;
                        }
                        var data = JSON.parse(res.responseText);
                        for (var key in data) {
                            data['__all__'] ?  org.ui.showSign(data['__all__']) : org.ui.showSign(data[key]);
                        }
                        lib._captcha_refresh()
                    },
                    complete: function() {
                        $submit.removeAttr('disabled').text('登录网利宝');
                    }
                });
                return false;
            });
        }
    }
    return {
        init : lib.init
    }


})(org);

org.regist = (function(org){
    var lib ={
        $captcha_img : $('#captcha'),
        $captcha_key : $('input[name=captcha_0]'),
        init:function(){
            lib._captcha_refresh();
            lib._checkFrom();
            lib._animateXieyi();
        },
        _animateXieyi:function(){
            var $submitBody = $('.submit-body'),
                $protocolDiv = $('.regist-protocol-div'),
                $cancelXiyi = $('.cancel-xiyie'),
                $showXiyi = $('.xieyi-btn'),
                $agreement = $('#agreement');
            //是否同意协议
            $agreement.change(function() {
              if ($(this).attr('checked') == 'checked') {
                $submitBody.addClass('disabled').attr('disabled', 'disabled');
                return $(this).removeAttr('checked');
              } else {
                $submitBody.removeClass('disabled').removeAttr('disabled');
                return $(this).attr('checked', 'checked');
              }
            });
            //显示协议
            $showXiyi.on('click',function(event){
                event.preventDefault();
                $protocolDiv.css('display','block');
                setTimeout(function(){
                    $protocolDiv.css('top','0%');
                },0)
            });
            //关闭协议
            $cancelXiyi.on('click',function(){
                $protocolDiv.css('top','100%');
                setTimeout(function(){
                    $protocolDiv.css('display','none');
                },200)
            })
        },
        _captcha_refresh :function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function(res) {
                lib.$captcha_img.attr('src', res['image_url']);
                lib.$captcha_key.val(res['key']);
            });
        },
        _checkFrom:function(){
            var $submit = $('button[type=submit]'),
                $identifier = $('input[name=identifier]'),
                $password = $('input[name=password]'),
                $validation =  $('input[name=validation]'),
                $invitation = $('input[name=invitation]'),
                $agreement = $('input[name=agreement]'),
                $captcha_0 =  $('input[name=captcha_0]'),
                $captcha_1 =  $('input[name=captcha_1]');


            org.ui.focusInput({
                submit : $submit,
                inputList: [
                    {target : $identifier,  required:true},
                    {target :$password,required : true},
                    {target: $validation,required : true},
                    {target: $invitation, required: false},
                    {target: $captcha_1, required: true}
                ],
                otherTarget : [{target: $agreement,required: true}]
            });
            $("#agreement").on('click',function(){
                $(this).toggleClass('agreement');
                $(this).hasClass('agreement') ?  $(this).find('input').attr('checked','checked') : $(this).find('input').removeAttr('checked');
                $identifier.trigger('input')
            })
            //刷新验证码
            lib.$captcha_img.on('click', function() {
                lib._captcha_refresh();
            });


            //手机验证码
            $('.request-check').on('click',function(){
                var phoneNumber = $identifier.val(),
                    $that = $(this), //保存指针
                    count = 60,  //60秒倒计时
                    intervalId ; //定时器

                if(!check['identifier'](phoneNumber, 'phone')) return  //号码不符合退出
                $that.attr('disabled', 'disabled').addClass('regist-alreay-request');
                org.ajax({
                    url : '/api/phone_validation_code/register/' + phoneNumber + '/',
                    data: {
                        captcha_0 : $captcha_0.val(),
                        captcha_1 : $captcha_1.val(),
                    },
                    type : 'POST',
                    error :function(xhr){
                        clearInterval(intervalId);
                        var result = JSON.parse(xhr.responseText);
                        org.ui.showSign(result.message);
                        $that.text('获取验证码').removeAttr('disabled').removeClass('regist-alreay-request');
                        lib._captcha_refresh();
                    }
                });
                //倒计时
                var timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return $that.text( count + '秒后可重发');
                    } else {
                        clearInterval(intervalId);
                        $that.text('重新获取').removeAttr('disabled').removeClass('regist-alreay-request');
                        return lib._captcha_refresh();
                    }
                };
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            });
            //校验方法
            var check ={
                identifier:function(val){
                    var isRight = false,
                        re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
                    re.test($.trim(val)) ? isRight = true : (org.ui.showSign('请输入正确的手机号'),isRight = false);
                    return isRight;
                },
                password:function(val){
                   if(6 > $.trim(val).length || $.trim(val).length > 20 ){
                       org.ui.showSign('密码为6-20位数字/字母/符号/区分大小写')
                       return false
                   }
                   return true
                }
            }
            var checkList = [$identifier, $password],
                isSubmit = true;

            var invite_phone = org.getQueryStringByName('parentPhone') == '' ? '' : org.getQueryStringByName('parentPhone');
            $submit.on('click',function(){
                isSubmit =  true;
                //校验主函数
                $.each(checkList, function(){
                    var value = $(this).val(), checkTarget = $(this).attr('name');
                    if(!check[checkTarget](value)){
                        return isSubmit = false
                    }
                });

                if(!isSubmit) return false;
                var tid = org.getQueryStringByName('tid');
                var token = $invitation.val() === '' ?  $('input[name=token]').val() : $invitation.val();
                org.ajax({
                    url: '/api/register/',
                    type: 'POST',
                    data: {
                            'identifier':       $identifier.val(),
                            'password':         $password.val(),
                            'captcha_0':        $captcha_0.val(),
                            'captcha_1':        $captcha_1.val(),
                            'validate_code':    $validation.val(),
                            'invite_code':      token,
                            'tid' : tid,
                            'invite_phone' : invite_phone
                    },
                    beforeSend: function() {
                        $submit.text('注册中,请稍等...');
                    },
                    success:function(data){
                        if(data.ret_code === 0){
                            //var next = org.getQueryStringByName('next') == '' ? '/weixin/regist/succees/?phone='+$identifier.val() : org.getQueryStringByName('next');
                            //next = org.getQueryStringByName('mobile') == '' ? next : next + '&mobile='+ org.getQueryStringByName('mobile');
                            //next = org.getQueryStringByName('serverId') == '' ? next : next + '&serverId='+ org.getQueryStringByName('serverId');
                            var next = '/weixin/sub_code/?phone='+$identifier.val();
                            window.location.href = next;
                        }else if(data.ret_code > 0){
                            org.ui.showSign(data.message);
                            $submit.text('立即注册 ｜ 领取奖励');
                        }
                    },
                    error: function (xhr) {
                        var result = JSON.parse(xhr.responseText);
                        if(xhr.status === 429){
                            org.ui.alert('系统繁忙，请稍候重试')
                        }else{
                            org.ui.alert(result.message);
                        }
                    },
                    complete:function(){
                        $submit.text('立即注册 ｜ 领取奖励');
                    }
                });
            })
        }
    }
    return {
        init : lib.init
    }
})(org);

;(function(org){
    $.each($('script'), function(){//登录、注册
        var src = $(this).attr('src');
        if(src && src.indexOf(org.scriptName) > 0){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    });
    org.detail.init();//下载、微信分享

    //关闭页面，返回微信
    function closePage(){
        if(typeof (WeixinJSBridge) != 'undefined'){
            WeixinJSBridge.call('closeWindow');
        }else{
            window.close();
        }
    }


    function timeFun(){//倒计时跳转
      var numDom = $("#times-box");
      var num = parseInt(numDom.text());
      var timeSet = setInterval(function(){
        if(num <= 0){
          clearInterval(timeSet);
          closePage();
          return;
        }
        num --;
        numDom.text(num+"秒");
      },1000);
    }
    window.onload = function(){
        timeFun();
        $("#unbind").addClass("clickOk");
        $("#no-unbind,.back-weixin").addClass("clickOk").click(function(){
            closePage();
        });
    }

    var unbindf = false;
    function unbingFun(){
        unbindf = true;
        var openid = $("#openid").val();
        org.ajax({
            type: "post",
            url: "/weixin/api/unbind/",
            data: {"openid":openid},
            dataType: "json",
            success: function (data) {
                //console.log(data);
                unbindf = false;
                window.location.href="/weixin/jump_page/?message=您已经解除绑定";
            }
        });
    }
    //解除绑定
    $("#unbind").click(function(){
        var self = $(this);
        if(unbindf){
            self.text("正在解除……");
            self.off("click");
            self.addClass("unbings")
        }else{
            self.text("解除绑定");
            self.on("click",unbingFun());
            self.removeClass("unbings")
        }
    });


    //关闭底部
    $("#footer-down").on("click",".down-close",function(){
        $("#footer-down").hide();
    });

    function btnAnimate(self,tp,k){
        var arrStr = ["终于等到你还好我没放弃","人品大爆发！"];
        var errorStr = ['太可惜了，你竟然与大奖擦肩而过','天苍苍，野茫茫，中奖的希望太渺茫','你和大奖只是一根头发的距离','奖品何时有，把酒问青天？','据说心灵纯洁的人中奖几率更高'];
        var noChance = '大奖明天见，网利宝天天见。您今天已经抽奖，明天再来碰运气吧';
        var btns = tp.find(".award-item");
        var i = 0;
        var num = 0;
        var alt = $("#alt-box");
        var altAwardP = alt.find("#alt-award-p");
        var altAward = altAwardP.find("#alt-award");
        var altPro = alt.find("#alt-promot");
        function setAn(){
            btns.eq(i).addClass("awards-now").siblings(".award-item").removeClass("awards-now");
            if(i === k && num > 1){
                clearInterval(setAnimate);
                setTimeout(function(){
                    $("#page-bg").show();
                    if(k === 0){
                        altPro.text(errorStr[Math.floor(Math.random()*5)]);
                        altAwardP.html('<span id="alt-award" class="alt-award">继续攒人品</span>');
                    }else{
                        altPro.text(arrStr[Math.floor(Math.random()*2)]);
                        altAward.text(btns.eq(i-1).text());
                    }
                    self.removeClass("had-click");
                    alt.show();
                },100);
            }
            if(i >= btns.length){
                num ++;
                clearInterval(setAnimate);
                i = 0;
                setAnimate = setInterval(setAn,100);
            }else{
              i ++;
            }
        }
        var setAnimate = setInterval(function(){
            setAn();
        },100);
    }
    var awardBtn = true;
    //立即抽奖
    $("#award-btn").click(function(){
        var self = $(this);
        if(awardBtn){
            awardBtn = false;
            self.addClass("had-click");
        }else{
            return;
        }
        var awards = self.parents("div.award-handle-box").siblings("div.award-btn-box");

        //awards.addClass("awards-now");
        btnAnimate(self,awards,3);
    });
    //关闭弹层
    $("#alt-box .close-box").click(function(){
        $(this).parents("#alt-box").hide();
        $("#page-bg").hide();
        awardBtn = true;
    });

    //规则 html添加class
    ;(function(){
        var html = $("html");
        //alert(html.height() + "," + $(window).height());
        if(html.height() <= $(window).height()){
            html.addClass("sub-height");
        }else{
            html.removeClass("sub-height");
        }
    })();
})(org);
function getCode(){//得到用户信息的二维码
    var phone = org.getQueryStringByName('phone');
    org.ajax({
        type: "POST",
        url: "/weixin/api/generate/qr_limit_scene_ticket/",
        data: {"original_id":"gh_9e8ff84237cd"},
        success: function (data) {
            $("#sub-code").html("<img src='"+ data.qrcode_url + "' />");
        },
        error: function(){
            window.location.href="/weixin/jump_page/?message=请进行登录并绑定您的微信";
        }
    });
}