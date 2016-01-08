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
                var earning, earning_element, earning_elements, fee_earning, jiaxi_type;
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
                jiaxi_type = target.attr('jiaxi-type');
                for (var i = 0; i < earning_elements.length; i ++) {
                    earning_element = earning_elements[i];
                    if (earning) {
                        fee_earning = fee_earning ? fee_earning : 0.00;
                        if(jiaxi_type === "+"){
                            $(earning_element).html(earning+'+<span class="blue">'+fee_earning+'</span>').data("val",(earning + fee_earning));
                        }else{
                            earning += fee_earning;
                            $(earning_element).text(earning.toFixed(2)).data("val",(earning + fee_earning));
                        }
                    } else {
                        //$(earning_element).text("0.00");
                        $(earning_element).html('0+<span class="blue">0.00</span>').data("val",0);
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
    };
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
        _alert: function(txt, callback, btn){
            if(typeof callback !="function" && typeof callback !="object"){
                btn = callback;
            }
            if(!btn){
                btn = "确认";
            }
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
                strHtml += " <div class='popub-footer' style='width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;'>"+ btn +"</div>";
                alertFram.innerHTML = strHtml;
                document.body.appendChild(alertFram);
                document.body.appendChild(shield);
                if(typeof callback == "object") {
                    //alert(callback.url);
                    $('.popub-footer').html('<a href="'+callback.url+'" style="display:block;">'+btn+'</a>');
                }else{
                   $('.popub-footer').on('click',function(){
                        alertFram.style.display = "none";
                        shield.style.display = "none";
                        (typeof callback == "function") && callback();
                    });
                }

            }
            document.body.onselectstart = function(){return false;};
        },
        _confirm: function(title, certainName, callback, callbackData){
            if($('.confirm-warp').length> 0 ){
                $('.confirm-text').text(title);
                $('.confirm-certain').text(certainName);
                $('.confirm-warp').show();

                $('.confirm-cancel').unbind('click').on('click', function(e){
                    $('.confirm-warp').hide();
                });
                $('.confirm-certain').unbind('click').on('click', function(e){
                    $('.confirm-warp').hide();
                    if(callback){
                        callbackData ? callback(callbackData): callback();
                    }
                })
            }
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
                            { target: $self.attr('data-target2'), addName : $self.attr('data-icon'), reMove : ($self.attr('data-icon')+"-active")}
                        ],$self);
                        $submit.attr('disabled', true);
                    }else{
                        inputForClass([
                            { target: $self.attr('data-target'), addName : $self.attr('data-val'),reMove : $self.attr('data-empty')},
                            { target: $self.attr('data-target2'), addName : ($self.attr('data-icon')+"-active"), reMove : $self.attr('data-icon')}
                        ],$self);
                    }
                    canSubmit() ? $submit.css('background','rgba(219,73,63,1)').removeAttr('disabled') : $submit.css('background','rgba(219,73,63,.5)').attr('disabled');
                    //canSubmit() ? $submit.css('background','#50b143').removeAttr('disabled') : $submit.css('background','rgba(219,73,63,.5)').attr('disabled');
                })
            });

            //用户名一键清空
            $('.identifier-edit').on('click', function(e){
                $(this).siblings().val('').trigger('input');
            });
            //密码隐藏显示
            $('.password-handle').on('click',function(){
                if($(this).hasClass('hide-password')){
                    $(this).addClass('show-password').removeClass('hide-password');
                    $(this).siblings().attr('type','text');
                }else if($(this).hasClass('show-password')){
                    $(this).addClass('hide-password').removeClass('show-password');
                    $(this).siblings().attr('type','password');
                }
            });

            var inputForClass = function(ops,t){
                if(!typeof(ops) === 'object') return ;
                var targetDom;
                $.each(ops, function(i){
                    if(t && t.siblings('.'+ops[i].target).length > 0){
                        targetDom = t.siblings('.'+ops[i].target);
                    }else{
                        targetDom = $('.'+ops[i].target);
                    }
                    targetDom.addClass(ops[i].addName).removeClass(ops[i].reMove);
                })
            };
            var returnCheckArr = function(){
                var returnArr = [];
                for(var i = 0; i < arguments.length; i++){
                    for(var arr in arguments[i]){
                        if(arguments[i][arr]['required'])
                          returnArr.push(arguments[i][arr]['target'])
                    }
                }
                return returnArr
            };
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
    };
    return {
        focusInput: lib._inputStyle,
        showSign : lib._showSign,
        alert : lib._alert,
        confirm: lib._confirm
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
                var host = 'https://www.wanglibao.com',
                    shareImg,//图片
                    shareLink,//连接地址
                    shareMainTit,//分享标题
                    shareBody,//分享描述
                    success;
                var conf = $.extend({
                    shareImg: host + '/static/imgs/sub_weixin/logo.png',//图片
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
                //alert(shareMainTit);
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg,
                    success: function(){
                        //alert(shareMainTit);
                    }
                });
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: shareMainTit,
                    link : shareLink,
                    imgUrl: shareImg,
                    success: function(){
                        //alert(shareMainTit);
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
    };
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
                    'password': $.trim($form.find('input[name=password]').val())
                    //'openid': $.trim($form.find('input[name=openid]').val())
                };
                org.ajax({
                    'type': 'post',
                    'url': $form.attr('action'),
                    'data': data,
                    beforeSend: function (xhr) {
                        $submit.attr('disabled', true).text('登录中..');
                    },
                    success: function(res) {
                        if(res.re_code != 0){
                            window.location.href = "/weixin/jump_page/?message="+res.errmessage;
                        }else{
                            window.location.href = "/weixin/jump_page/?message=您已登录并绑定成功";
                        }
                        //org.ajax({
                        //   'type': 'post',
                        //    'url': '/weixin/api/bind/',
                        //    'data': {'openid': data.openid},
                        //    success: function(data){
                        //        console.log(data.message);
                        //        window.location.href = "/weixin/jump_page/?message=" + data.message;
                        //    },
                        //    error: function(data){
                        //        window.location.href = "/weixin/jump_page/?message=" + data.message;
                        //    }
                        //});
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
                        $submit.removeAttr('disabled').text('登录并关联网利宝账号');
                    }
                });
                return false;
            });
        }
    };
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
            });
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

                if(!check['identifier'](phoneNumber, 'phone')) return;  //号码不符合退出
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
                       org.ui.showSign('密码为6-20位数字/字母/符号/区分大小写');
                       return false
                   }
                   return true
                }
            };
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
                        'invite_phone' : invite_phone,
                        'register_channel': "fwh"
                    },
                    beforeSend: function() {
                        $submit.text('注册中,请稍等...');
                    },
                    success:function(data){
                        if(data.ret_code === 0){
                            //var next = org.getQueryStringByName('next') == '' ? '/weixin/sub_regist_first/?phone='+$identifier.val() : org.getQueryStringByName('next');
                            var next = '/weixin/sub_regist_first/?phone='+$identifier.val();
                            next = org.getQueryStringByName('mobile') == '' ? next : next + '&mobile='+ org.getQueryStringByName('mobile');
                            next = org.getQueryStringByName('serverId') == '' ? next : next + '&serverId='+ org.getQueryStringByName('serverId');
                            //console.log(next);
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
    };
    return {
        init : lib.init
    }
})(org);

org.list = (function(org){
    var lib = {
        windowHeight : $(window).height(),
        canGetPage : true, //防止多次请求
        scale : 0.8, //页面滚到百分70的时候请求
        pageSize: 10, //每次请求的个数
        page: 2, //从第二页开始
        init :function(){
            lib._scrollListen();
        },
        _scrollListen:function(){
            $('.load-body').on('click', function(){
                lib.canGetPage && lib._getNextPage();
            })
        },
        _getNextPage :function(){
            var loadDom = $(".list-load .load-body");
            org.ajax({
                type: 'GET',
                url: '/weixin/api/fwh/p2p_ajax_list/',
                data: {page: lib.page, 'pagesize': lib.pageSize},
                beforeSend:function(){
                    lib.canGetPage =false;
                    loadDom.find('.load-text').html('加载中...');
                },
                success: function(data){
                    if(data.html_data === ""){
                        loadDom.hide();
                    }else{
                        $('#list-body').append(data.html_data);
                    }
                    lib.page++;
                    lib.canGetPage = true;
                },
                error: function(){
                    org.ui.alert('Ajax error!')
                },
                complete: function(){
                     $('.load-text').html('点击查看更多项目');
                }
            })
        }

    };
    return {
        init : lib.init
    }
})(org);

org.buy=(function(org){
    var lib = {
        redPackSelect : $('#gifts-package'),
        amountInout : $('input[data-role=p2p-calculator]'),
        $redpackSign : $('.redpack-sign'),
        $redpackForAmount : $('.redpack-for-amount'),
        showredPackAmount:$(".redpack-amount"),
        showAmount :$('.need-amount'),
        redPackAmount: 0,
        isBuy: true, //防止多次请求，后期可修改布局用button的disable，代码罗辑会少一点
        init :function(){
            lib._checkRedpack();
            lib._calculate();
            lib._buy();
            lib._amountInp();
        },
        _amountInp: function(){ //金额输入
            lib.amountInout.on("input",function(){
                var self = $(this),
                    val = self.val();
                if(val != ""){
                    $(".snap-up").removeAttr("disabled").css("opacity",1);
                }else{
                    $(".snap-up").attr("disabled",true).css("opacity",0.5);
                }
                lib._setRedpack();
                //lib.showAmount.text(val);
            });
        },
        _checkRedpack: function(){
            var productID = $(".invest-one").attr('data-protuctid');
            org.ajax({
                type: 'POST',
                url: '/api/redpacket/selected/',
                data: {product_id: productID},
                success: function(data){
                    if(data.ret_code === 0 ){
                        if(data.used_type == 'redpack')
                             $('.redpack-already').html(data.message).show();
                        else if (data.used_type == 'coupon'){
                            lib.amountInout.attr('activity-jiaxi', data.amount);
                            $('.redpack-already').show().find('.already-amount').text(data.amount + '%');
                        }

                    }
                }
            });
        },
        /*
        * 购买页收益计算器
         */
        _calculate:function(){
            org.calculate(lib.amountInout,lib._setRedpack)
        },
        /*
        *   购买提示信息
        *   触发_setRedpack条件 选择红包，投资金额大于0
        *
        *
         */
        _setRedpack:function(){
            var redPack = lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex),//选择的select项
                redPackVal = parseFloat(lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex).attr('data-amount'));
                inputAmount  =parseInt(lib.amountInout.val()), //输入框金额
                redPackAmount = redPack.attr("data-amount"), //红包金额
                redPackMethod = redPack.attr("data-method"), //红包类型
                redPackInvestamount = parseInt(redPack.attr("data-investamount")),//红包门槛
                redPackHighest_amount = parseInt(redPack.attr("data-highest_amount")),//红包最高抵扣（百分比红包才有）
                repPackDikou = 0,
                senderAmount = inputAmount; //实际支付金额;

            lib.redPackAmountNew = 0 ;
            inputAmount = isNaN(inputAmount) ? "0.00" : inputAmount;
            if(redPackVal){ //如果选择了红包
                if(!inputAmount){
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    //lib.$redpackSign.hide();//红包直抵提示
                    lib.showAmount.text(inputAmount);//实际支付
                    return
                }

                if(inputAmount < redPackInvestamount){
                    lib.$redpackSign.hide();//红包直抵提示
                    lib.$redpackForAmount.hide();//请输入投资金额
                    //lib.showAmount.text(senderAmount);//实际支付金额
                    $(".redpack-investamount").show();//未达到红包使用门槛
                }else{
                    lib.amountInout.attr('activity-jiaxi', 0);
                    if(redPackMethod == '*'){ //百分比红包
                        //如果反回来的百分比需要除于100 就把下面if改成if (inputAmount * redPackAmount/100 > redPackHighest_amount)
                        if(inputAmount * redPackAmount >= redPackHighest_amount && redPackHighest_amount > 0){//是否超过最高抵扣
                           repPackDikou = redPackHighest_amount;
                        }else{//没有超过最高抵扣
                            repPackDikou = inputAmount * redPackAmount;
                        }
                    }else if(redPackMethod == '~'){
                        lib.amountInout.attr('activity-jiaxi', redPackAmount * 100);
                        repPackDikou = 0;
                        lib.$redpackSign.hide();
                    }else{  //直抵红包
                        repPackDikou = parseInt(redPackAmount);
                    }
                    senderAmount = inputAmount - repPackDikou;
                    lib.redPackAmountNew = repPackDikou;
                    if(redPackMethod != '~'){
                        lib.showredPackAmount.text(repPackDikou);//红包抵扣金额
                        lib.$redpackSign.show();//红包直抵提示
                    }
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                }
            }else{
                lib.$redpackSign.hide();//红包直抵提示
            }
            senderAmount = isNaN(senderAmount) ? "0.00" : senderAmount;
            lib.showAmount.text(senderAmount);//实际支付金额
            lib.$redpackForAmount.hide();//请输入投资金额
            //income.html((rate * dataRate) +'+<span class="blue">'+ (rate * jiaxi) +'</span>');
        },
        _goBuy: function(cfg){
            var $buyButton = $('.snap-up');
            var productID = cfg.productID,
                amount = cfg.amount,
                redpackValue = cfg.redpackValue,
                balance = cfg.balance;
            org.ajax({
                type: 'POST',
                url: '/api/p2p/purchase/?v='+Math.random(),
                data: {product: productID, amount: amount, redpack: redpackValue},
                beforeSend:function(){
                    $buyButton.text("抢购中...");
                    lib.isBuy = false;
                },
                success: function(data){
                   if(data.data){
                       //$('.balance-sign').text(balance - data.data + lib.redPackAmountNew + '元');
                       //$(".sign-main").css("display","-webkit-box");
                       $("#page-ok").css('display','-webkit-box');
                   }
                },
                error: function(xhr){
                    var result;
                    result = JSON.parse(xhr.responseText);
                    if(xhr.status === 400){
                        if (result.error_number === 1) {
                            org.ui.alert("登录超时，请重新登录！",function(){
                                //return window.location.href= '/weixin/sub_login/?next=/weixin/sub_detail/detail/'+productID+'/';
                            });
                        } else if (result.error_number === 2) {
                            return org.ui.alert('必须实名认证！');
                        } else if (result.error_number === 4 && result.message === "余额不足") {
                            //$(".buy-sufficient").show();
                            $("#page-onMoney").show();
                        }else{
                            return org.ui.alert(result.message);
                        }
                    }else if(xhr.status === 403){
                        if (result.detail) {
                            org.ui.alert("登录超时，请重新登录！",function(){
                                return window.location.href = '/weixin/sub_login/?next=/weixin/sub_detail/detail/' + productID + '/';
                            });
                        }
                    }
                },
                complete:function(){
                    $buyButton.text("立即投资");
                    lib.isBuy = true;
                }
            })
        },
        _buy:function(){
            var $buyButton = $('.snap-up'),
                $redpack = $("#gifts-package");//红包
            //红包select事件
            $redpack.on("change",function(){
                if($(this).val() != ''){
                    lib.amountInout.val() == '' ?  $('.redpack-for-amount').show(): lib._setRedpack();
                }else{
                    lib.amountInout.attr('activity-jiaxi', 0);
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    lib.$redpackSign.hide();
                }
                return lib.amountInout.trigger('input');
            });

            $buyButton.on('click',function(){
                var $buySufficient = $('#page-onMoney'),
                    balance = parseFloat($("#balance").attr("data-value")),//当前余额
                    amount = $('.amount').val() *1,//投资金额
                    productID = $(".invest-one").attr('data-protuctid');//投资项目id
                //var self = $(this);
                if(amount){
                    //console.log(amount > balance, amount, balance, $buySufficient.length);
                    if(amount % 100 !== 0) return org.ui.alert('请输入100的倍数金额');
                    if(amount > balance)  return $buySufficient.show();
                }else{
                     return org.ui.alert('请输入正确的金额');
                }
                var redpackDom = $redpack[0].options[$redpack[0].options.selectedIndex],
                    minAmount = $(redpackDom).attr("data-investamount"),
                    redpackValue = redpackDom.value;
                if(minAmount && amount<minAmount){
                    return org.ui.alert('未达到红包使用门槛');
                }
                if(!redpackValue || redpackValue == ''){
                    redpackValue = null;
                }
                var postdata = {
                    productID: productID,
                    amount: amount,
                    redpackValue: redpackValue,
                    balance: balance
                };
                var pageOption = {//设置交易密码 参数
                    page: $("#page-pwd"),
                    title: "设置交易密码",
                    cont: "为了您账户资金安全，请设置交易密码",
                    type: "投资",
                    amount: amount,
                    callBack: setTradePwd,
                    callBackOpt: postdata
                };
                var inputOption = { //输入交易密码 参数
                    type: "投资",
                    amount: amount,
                    callBack: "none",
                    callBackOpt: postdata
                };
                if(lib.isBuy){

                    org.ui.confirm("购买金额为" + amount, '确认投资', lib._goBuy, postdata);//使用交易密码时删除

                    //org.ajax({ //交易密码，使用时去掉注释
                    //    url: '/api/profile/',
                    //    type: 'GET',
                    //    success:function(data){
                    //        if(data.trade_pwd_is_set){
                    //            //org.setInputPwd.inputPwd("充值",amount);
                    //            isFirstPwd = false;
                    //            org.setInputPwd.inputPwd(inputOption);//投资
                    //        }else{
                    //            isFirstPwd = true;
                    //            org.setInputPwd.pageSet(pageOption);//首次交易
                    //        }
                    //    },
                    //    error: function (xhr) {
                    //        console.log("标记用用户是否已经设置交易密码失败",xhr);
                    //    }
                    //});

                }else{
                    org.ui.alert("购买中，请稍后")
                }
            })
        }
    };
    return {
        init : lib.init,
        goBuy: lib._goBuy
    }
})(org);

org.calculator=(function(org){
    var lib = {
        init :function(){
            org.calculate($('input[data-role=p2p-calculator]'));
            lib._addEvenList();
        },
        _addEvenList:function(){
            var $calculatorBuy = $('.calculator-buy'),
                $countInput = $('.count-input'),
                productId, amount_profit, amount;

            $calculatorBuy.on('click',function(){
                productId = $(this).attr('data-productid');
                amount  = $countInput.val();
                amount_profit = $("#expected_income").text();
                if(amount % 100 !== 0 || amount == ''){
                    return org.ui.alert("请输入100的整数倍")
                }else{
                    //window.location.href = '/weixin/view/buy/' + productId + '/?amount='+ amount + '&amount_profit=' + amount_profit;
                }
            })
        }
    };
    return {
        init : lib.init
    }
})(org);
var isFirstPwd = true;//true:设置交易密码，false:输入交易密码
org.setInputPwd = (function(org){//交易密码
    var lib = {
        type: "充值",//充值or投资
        amount: 0,
        /*
        * 交易密码
         */
        _pageSet: function(cfg){//设置密码弹出层 文本设置
            lib.type = cfg.type;//充值or投资
            //lib.isFirst = cfg.isFirst;//是否是第一次
            lib.amount = cfg.amount; //金额
            cfg.page.find(".pwd-tit").html(cfg.title);
            cfg.page.find(".pwd-promote").html(cfg.cont);
            cfg.page.show();
            lib._inputPwd(cfg.callBack,cfg.callBackOpt);//弹层js
            cfg.page.find(".js-pwd-inps").trigger("click touchstart");
        },
        _pwdAnimate: function(inp,callBack,postdata){//交易密码弹出层 显示
            var startVal = '';
            var page = inp.parents("#page-pwd");
            var pageOption = {
                page: page,
                title: "设置交易密码",
                cont: "请再次确认交易密码",
                type: lib.type,
                amount: lib.amount,
                callBack: callBack,
                callBackOpt: postdata
            };
            inp.on("input",function(){
                var self = $(this);
                var val = self.val();
                if(val.length >= 6) {
                    if(isFirstPwd){
                        if (page.data("num") !== 1) {
                            page.data("num", 1).hide();
                            startVal = val;
                            self.val("");
                            //lib._pageSet(page, "设置交易密码", "请再次确认交易密码", lib.type, true, callBack);
                            lib._pageSet(pageOption);
                        } else {
                            page.data("num", 2).hide();
                            self.val("");
                            if(val !== startVal){
                                $("#page-error").show();//密码两次输入不一致
                            }else{
                                //------------此处密码输入后的函数-------------//
                                callBack && callBack(val,postdata,lib.type);
                                //if(callBack && callBack(val)){
                                //    console.log(2,postdata);
                                //    org.recharge.rechargeSingleStep(postdata,val);
                                //}
                                //$("#page-net").show();//网络断开
                            }
                        }
                    }else{
                        lib._inpPwdHide(self);
                        //------------此处密码输入后的函数-------------//
                        if(lib.type === "投资"){
                            org.buy.goBuy(postdata);
                        }else{
                            org.recharge.rechargeSingleStep(postdata,val);
                        }
                        //org.ui.confirm("交易密码输入不正确，您还可以输入2次", "重新输入", lib._inpPwdShow, lib.amount);//密码错误
                        //org.ui.alert("<p class='lock-pwd'>交易密码已被锁定，请3小时后再试<br />如想找回密码，请通过网站或APP找回</p>", closePage,  "知道了");
                        //if(lib.type === "充值"){
                        //    $("#page-ok").show().find("#total-money").text("11800");//密码正确
                        //}else{
                        //    $("#page-ok").show();
                        //}

                    }
                }
            });
        },
        _inpPwdShow: function(opt){//显示 输入交易密码
            var pageOption = {
                page: $("#page-pwd"),
                title: "请输入交易密码",
                cont: opt.type + "金额<br />￥" + opt.amount,
                type: opt.type,
                amount: opt.amount,
                callBack: opt.callBack,
                callBackOpt: opt.callBackOpt
            };
            lib._pageSet(pageOption);
        },
        _inpPwdHide: function(self){//隐藏 交易密码
            var tp = self.parents(".page-alt");
            var pwd = tp.find("input.pwd-input");
            tp.hide();
            pwd.length > 0 ? pwd.val(""): "";
        },
        _inpMoveEnd: function(obj){//input最后位置获取焦点
            obj.focus();
            var len = obj.val().length;
            if (document.selection) {
                var sel = obj.createTextRange();
                sel.moveStart('character', len);
                sel.collapse();
                sel.select();
            } else if (typeof obj.selectionStart == 'number'&& typeof obj.selectionEnd == 'number') {
                obj.selectionStart = obj.selectionEnd = len;
            }
        },
        _inputPwd: function(callBack,postdata){
            var inpDom = $(".js-pwd-inps");
            var inp = inpDom.find("input.pwd-input");
            inpDom.on("click touchstart",function(e){//点击弹出层输入框
                e.stopPropagation();
                e.preventDefault();
                inp.focus();
                lib._inpMoveEnd(inp);
            });
            lib._pwdAnimate(inp,callBack,postdata);
            $(".page-close").on("click",function(){//关闭弹出层
                lib._inpPwdHide($(this));
            });
            $(".back-fwh").on("click",function(){
                lib._inpPwdHide($(this));
                closePage();
            });
            $(".continue-rechare").on("click",function(){//继续充值
                lib._inpPwdHide($(this));
                $("input.count-input").val("");
            });
        }
    };

    return {
        //init: lib.init,
        pageSet: lib._pageSet,
        inputPwd: lib._inpPwdShow
    }
})(org);
function setTradePwd(pwd,postdata,type){
    if(typeof postdata != "object"){
        type = postdata;
        postdata = {};
    }
    org.ajax({
        url: '/api/trade_pwd/',
        type: 'post',
        data: {"action_type":1,"new_trade_pwd":pwd},
        dataType : 'json',
        success:function(){
            if(type === "投资"){
                org.buy.goBuy(postdata);
            }else{
                org.recharge.rechargeSingleStep(postdata,pwd);
            }
        },
        error: function (xhr) {
            console.log("设置交易密码失败",xhr);
            //code = data.ret_code;
        }
    });
}
;(function(){ //关闭弹出层，待交易密码上的时候删除此函数
    function inpPwdHide(self){//隐藏 交易密码
        var tp = self.parents(".page-alt");
        var pwd = tp.find("input.pwd-input");
        tp.hide();
        pwd.length > 0 ? pwd.val(""): "";
    }
    $(".page-close").on("click",function(){//关闭弹出层
        inpPwdHide($(this));
    });
    $(".back-fwh").on("click",function(){
        inpPwdHide($(this));
        closePage();
    });
    $(".continue-rechare").on("click",function(){//继续充值
        inpPwdHide($(this));
        $("input.count-input").val("");
    });
})(org);
org.recharge=(function(org){
    var lib = {
        canRecharge: true,
        cardInput: $("#card-val"),
        bankName: $(".bank-txt-name"),
        amountInput: $("input.count-input"),
        maxamount: $("input[name=maxamount]"),
        firstBtn: $('#firstBtn'),
        secondBtn: $('#secondBtn'),
        init :function(){
            lib._getBankCardList();
            lib._rechargeStepFirst();
            lib._initBankNav();
            //lib._inputPwd();
        },
        /*
        * 充值nav动画及事件触发
        */
        _initBankNav:function(){
            var $nav = $(".bank-list-nav"),
                $cardNone = $('.card-none'),
                $cardHave = $('.card-have');
            $nav.css("-webkit-transform","translate3d(10.2rem,0,0)");
            $nav.on('click',function(e){
                var $targetName = e.target.className.split(' ')[1];
                switch ($targetName){
                    case 'bank-add':
                        closeNav(function(){
                            $cardHave.hide();
                            setTimeout(function(){
                                $cardHave.css("opacity",0);
                                $cardNone.show();
                                setTimeout(function(){
                                    $cardNone.css("opacity",1)
                                },50)
                            },50)
                        });
                        break;
                    case 'bank-card':

                        closeNav();
                        break;
                    case 'bank-cancel':
                        closeNav();
                        break
                }

            });
            function closeNav(callback){
                $nav.css("-webkit-transform","translate3d(10.2rem,0,0)");
                callback && callback();
            }
        },
        /*
        * 页面初始化判断是否首次充值
         */
        _getBankCardList: function(){
            var $cardNone = $('.card-none'),
                $cardHave = $('.card-have');
            org.ajax({
                type: 'POST',
                url: '/api/pay/cnp/list/',
                success: function(data) {
                    //如果支付接口有返回已绑定的银行列表，将银行列表写入网页，银行卡：data.cards
                    if(data.ret_code == 0){
                        $(".recharge-loding").hide();
                        if(data.cards.length === 0){
                            $cardNone.show();
                            setTimeout(function(){
                                $cardNone.css("opacity",1)
                            },50)
                        }else if(data.cards.length > 0){
                            lib._initCard(data.cards,lib._cradStyle(data.cards));
                            $cardHave.show();
                            setTimeout(function(){
                                $cardHave.css("opacity",1)
                            },50);
                        }
                    }
                }
            });
            $(".bank-txt-right").on('click',function(){
                 //$(".bank-list-nav").css("-webkit-transform","translate3d(0,0,0)");
                $('.recharge-select-bank').css('display','-webkit-box');
            });
        },
        /*
        *  初始化默认银行卡，没有默认银行卡，现在为第一个，回调函数为银行卡列表
         */
        _initCard:function(data, callback){
            var oneMax = 50000;
            lib.cardInput.val(data[0]['storable_no'].slice(0,6) + '********'+ data[0]['storable_no'].slice(-4)).attr('data-storable', data[0]['storable_no']);
            lib.bankName.text(data[0]['bank_name']);
            if(lib.firstBtn.css("display") != "none"){
                oneMax = data[0].first_one;
            }else{
                oneMax = data[0].second_one;
            }
            lib.amountInput.attr({"placeholder":"该银行单笔限额"+ oneMax/10000 +"万元"});
            lib.maxamount.val(oneMax);
            callback && callback();
        },
        /*
        * 银行卡列表
         */
        _cradStyle:function(cardList){
            var str = '';
            if(cardList.length === 1){
                $(".js-bank-img").hide();
            }
            for(var card in cardList){
                str += "<div class= 'select-bank-list' data-storable="+cardList[card].storable_no+" data-bankName="+ cardList[card].bank_name +" data-maxNum="+ cardList[card].second_one +">";
                str += cardList[card].bank_name + "(" + cardList[card].storable_no.slice(-4) + ")";
                str += "</div>";
            }
            $(".select-bank-cont").append(str);
            $('.select-bank-list').on('click',function(event){
                var that = this;
                var oneMax = $(that).attr("data-maxNum");
                lib.cardInput.val($(that).attr("data-storable").slice(0,6) + '********'+ $(that).attr("data-storable").slice(-4)).attr('data-storable', $(that).attr("data-storable"));
                lib.bankName.text($(that).attr("data-bankName"));
                lib.amountInput.attr({"placeholder":"该银行单笔限额"+ oneMax/10000 +"万元"});
                lib.maxamount.val(oneMax);
            });
            $(".recharge-select-bank").on('click',function(){
                 return $(this).hide();
            })
        },
        /*
        *   $firstBtn 为首次充值 进到一下步
        *   $secondBtn 为快捷充值
         */
        _rechargeStepFirst:function(){
            var card_no, gate_id, amount, maxamount,
                $firstBtn = lib.firstBtn,
                $secondBtn = lib.secondBtn;

            $firstBtn.on('click', function(){
                card_no = $("input[name='card_none_card']").val(),
                gate_id = $("select[name='gate_id_none_card']").val(),
                amount  = $("input[name='amount']").val() * 1,
                maxamount = parseInt($("input[name='maxamount']").val());
                if(!card_no || !gate_id || amount <= 0 || !amount) {
                    return org.ui.alert('信息输入不完整');
                }
                if(amount > maxamount){
                     return org.ui.alert('最高充值'+ maxamount +'元！')
                }
                window.location.href = '/weixin/recharge/second/?rechargeNext='+$(this).attr('data-next')+'&card_no=' + card_no + '&gate_id=' + gate_id + '&amount=' + amount;
            });
            $secondBtn.on('click', function(){
                card_no = $("input[name='card_no']").attr('data-storable'),
                amount  = $("input[name='amount']").val() * 1,
                maxamount = parseInt($("input[name='maxamount']").val());
                if(!card_no || amount <= 0 || !amount) {
                    return org.ui.alert('信息输入不完整');
                }
                if(amount < 10){
                    return org.ui.alert('充值金额不得少于10元');
                }
                if(amount > maxamount){
                     return org.ui.alert('最高充值'+ maxamount +'元！');
                }
                if(lib.canRecharge){
                    var postdata = {
                        card_no: card_no,
                        amount: amount
                    };
                    var pageOption = {//设置交易密码 参数
                        page: $("#page-pwd"),
                        title: "设置交易密码",
                        cont: "为了您账户资金安全，请设置交易密码",
                        type: "充值",
                        amount: amount,
                        callBack: setTradePwd,
                        callBackOpt: postdata
                    };
                    var inputOption = { //输入交易密码 参数
                        type: "充值",
                        amount: amount,
                        callBack: "none",
                        callBackOpt: postdata
                    };
                    //org.ajax({ //用用户是否已经设置交易密码
                    //    url: '/api/profile/',
                    //    type: 'GET',
                    //    success:function(data){
                    //        if(data.trade_pwd_is_set){
                    //            isFirstPwd = false;
                    //            org.setInputPwd.inputPwd(inputOption);//充值
                    //        }else{
                    //            isFirstPwd = true;
                    //            org.setInputPwd.pageSet(pageOption);//首次充值
                    //        }
                    //    },
                    //    error: function (xhr) {
                    //        console.log("标记用用户是否已经设置交易密码失败",xhr);
                    //    }
                    //});
                    org.ui.confirm("充值金额为"+amount, '确认充值', lib._rechargeSingleStep, postdata);//使用交易密码时删除

                }else{
                    return org.ui.alert('充值中，请稍后');
                }
            });
        },
        /*
        * 快捷充值接口业务
         */
        //_rechargeSingleStep: function(getdata,pwd) {//有交易密码
        _rechargeSingleStep: function(getdata) {
            org.ajax({
                type: 'POST',
                //url: '/api/pay/deposit_new/',//有交易密码
                //data: {card_no: getdata.card_no, amount: getdata.amount, trade_pwd: pwd},
                url: '/api/pay/deposit/',
                data: {card_no: getdata.card_no, amount: getdata.amount},
                beforeSend:function(){
                    lib.canRecharge = false;
                    $('#secondBtn').text("充值中..");
                },
                success: function(data) {
                    if(data.ret_code > 0) {
                        return org.ui.alert(data.message);
                    } else {
                        $('#page-ok').css('display','-webkit-box').find("#total-money").text(data.margin);
                        $(".bank-account-num span.num").text(data.margin);
                    }
                },
                error:function(data){
                    if(data.status == 403){
                        org.ui.alert('登录超时，请重新登录！');
                    }
                },
                complete:function(){
                    $('#secondBtn').text("立即充值");
                    lib.canRecharge = true;
                }
            })
        }
    };
    return {
        init : lib.init,
        rechargeSingleStep: lib._rechargeSingleStep
    }
})(org);
/*
* 首次充值进入下一个页面的业务
 */
org.recharge_second=(function(org){
    var lib = {
        card_no : $("input[name='card_no']").val(),
        gate_id : $("input[name='gate_id']").val(),
        amount  : parseInt($("input[name='amount']").val()),
        phone: null,
        init :function(){
            lib._getValidateCode();
            lib._rechargeStepSecond();
        },
        _getValidateCode: function(){
            var getValidateBtn = $('.request-check');

            getValidateBtn.on('click', function(){
                var count = 180, intervalId ; //定时器
                var re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
                lib.phone = $("input[name='phone']").val();
                lib.card_no = $("input[name='card_no']").val();

                if(!lib.phone){
                    return org.ui.alert('请填写手机号');
                }
                if(!re.test(lib.phone)){
                    return org.ui.alert('请填写正确手机号');
                }

                getValidateBtn.attr('disabled', 'disabled').addClass('alreay-request');
                //倒计时
                var timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return getValidateBtn.text( count + '秒后可重发');
                    } else {
                        clearInterval(intervalId);
                        getValidateBtn.text('重新获取').removeAttr('disabled').removeClass('alreay-request');

                    }
                };

                org.ajax({
                    type: 'POST',
                    url: '/api/pay/deposit/',
                    data: {card_no: lib.card_no, gate_id: lib.gate_id, phone: lib.phone, amount: lib.amount},
                    success: function(data) {
                        if(data.ret_code > 0) {
                            clearInterval(intervalId);
                            getValidateBtn.text('重新获取').removeAttr('disabled').removeClass('alreay-request');
                            return org.ui.alert(data.message);
                        } else {
                            //alert('验证码已经发出，请注意查收！');
                            $("input[name='order_id']").val(data.order_id);
                            $("input[name='token']").val(data.token);
                        }
                    },
                    error:function(data){
                        console.log(data)
                    }
                });
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            })
        },
        _rechargeStepSecond:function(){
            var secondBtn = $('#secondBtn'),
                canPost = true,
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
            secondBtn.on('click', function(){
                var order_id = $("input[name='order_id']").val(),
                    vcode = $("input[name='vcode']").val(),
                    token = $("input[name='token']").val(),
                    amount = $("input[name='amount']").val();
                if(!lib.phone){
                    return org.ui.alert('请填写手机号');
                }
                if(!re.test(lib.phone)){
                    return org.ui.alert('请填写正确手机号');
                }
                if(!vcode){
                    return org.ui.alert('请输入手机验证码');
                }
                if(!order_id || !token) {
                    return org.ui.alert('系统有错误，请重试获取验证码');
                }

                if(canPost){
                    org.ui.confirm("充值金额为" + amount, '确认充值', recharge);
                    function  recharge(){
                        org.ajax({
                            type: 'POST',
                            url: '/api/pay/cnp/dynnum/',
                             data: {phone: lib.phone, vcode: vcode, order_id: order_id, token: token},
                            beforeSend:function(){
                                canPost = false;
                                secondBtn.text("充值中...");
                            },
                            success: function(data) {
                                if(data.ret_code > 0) {
                                    return org.ui.alert(data.message);
                                } else {
                                   $('.sign-main').css('display','-webkit-box').find(".balance-sign").text(data.amount);
                                }
                            },
                            complete:function(){
                                canPost = true;
                                secondBtn.text("充值");
                            }
                        })
                    }
                }else{
                    return org.ui.alert('充值中，请稍后');
                }
            })
        }
    };
    return {
        init : lib.init
    }
})(org);

org.authentication = (function(org){
    var lib = {
        isPost: true,
        $fromComplete : $(".from-four-complete"),
        init: function(){
            lib._checkForm();
        },
        _checkForm :function(){
            var formName = ['name','id_number'],
                formError = ['.error-name', '.error-card'],
                formSign = ['请输入姓名', '请输入身份证号', '请输入有效身份证'],
                data = {},
                reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/; //身份证正则

            lib.$fromComplete.on('click',function(){
                var isFor = true;
                $('.sign-all').hide();
                $('.check-input').each(function(i){
                    if(!$(this).val()){
                        isFor =false;
                        return $(formError[i]).text(formSign[i]).show();
                    }else{
                        if(i === 1 && !reg.test($(this).val())){
                            isFor =false;
                            return $(formError[i]).text(formSign[2]).show();
                        }
                    }
                    data[formName[i]] = $(this).val();
                });
                isFor && lib._forAuthentication(data)
            });
        },
        _forAuthentication:function(ags){
            if(lib.isPost){
                org.ajax({
                    type: 'POST',
                    url : '/api/id_validate/',
                    data : ags,
                    beforeSend:function(){
                        lib.isPost = false;
                        lib.$fromComplete.text("认证中，请等待...");
                    },
                    success:function(){
                        //org.ui.alert("实名认证成功!",function(){
                        //   return window.location.href = '/weixin/account/';
                        //});
                        org.ui.alert("实名认证成功!",{url:'/weixin/sub_account/'});
                    },
                    error:function(xhr){
                        result = JSON.parse(xhr.responseText);
                        return org.ui.alert(result.message);
                    },
                    complete:function(){
                        lib.isPost = true;
                        lib.$fromComplete.text("完成");
                    }
                })
            }
        }
    };
    return {
        init :lib.init
    }
})(org);

org.bankcardAdd = (function(org){
    var lib = {
        init:function(){
            lib._checkForm();
        },
        _checkForm:function(){
            var reg = /^\d{10,20}$/;
            $(".addBank-btn").on('click',function(){
                var gate_id = $('#bank-select').val(),
                    card_number = $('#card-no').val(),
                    is_default = $('#default-checkbox').prop('checked');

                if (!gate_id) {
                    return org.ui.alert('请选择银行');
                }
                if(!reg.test(card_number)){
                    return org.ui.alert('请输入有效的银行卡号')
                }
                var data =  {
                  card_number: card_number,
                  gate_id : gate_id,
                  is_default : is_default
                };

                lib._forAddbank(data);
            });
        },
        _forAddbank:function(data){
            org.ajax({
                type: "POST",
                url: '/api/bank_card/add/',
                data: data,
                beforeSend:function(){
                   $(".addBank-btn").attr("disabled","true").text("添加中...");
                },
                success:function(result){
                    if(result.ret_code === 0){
                        org.ui.alert("添加成功！",function(){
                             window.location.href = '/weixin/account/bankcard/';
                        });
                    }else if(result.ret_code > 0){
                        org.ui.alert(result.message);
                    }
                },
                error:function(result){
                    if (result.error_number === 6) {
                      return org.ui.alert(result.message);
                    }else{
                        return org.ui.alert("添加银行卡失败");
                    }
                },
                complete:function(){
                    $(".addBank-btn").removeAttr("disabled").text("添加银行卡");
                }

            })
        }
    };
    return {
        init : lib.init
    }
})(org);

org.processFirst = (function(org){
    var lib = {
        $submit : $('button[type=submit]'),
        $name : $('input[name=name]'),
        $idcard : $('input[name=idcard]'),
        init:function(){
            lib._form_logic();
            lib._postData();
        },
        _form_logic: function(){
            var _self = this;

            org.ui.focusInput({
                submit : _self.$submit,
                inputList: [
                    {target : _self.$name,  required:true},
                    {target : _self.$idcard, required : true}
                ]
            });
        },

        _postData :function(){
            var _self = this, data = {};
            _self.$submit.on('click',function(){
                data = {
                    name: _self.$name.val(),
                    id_number: _self.$idcard.val()
                };
                _self._check($('.check-list')) && _self._forAuthentication(data)
            });



        },
        _check: function(checklist){
            var check = true,
                reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;

            checklist.each(function(i){
                if($(this).val() == ''){
                    org.ui.showSign($(this).attr('placeholder'));
                    return check = false;
                }else{
                    if(i === 1 && !reg.test($(this).val())){
                        org.ui.showSign('请输入正确的身份证号');
                        return check =false;
                    }
                }
            });

            return check
        },
        _forAuthentication:function(postdata){
            org.ajax({
                type: 'POST',
                url : '/api/id_validate/',
                data : postdata,
                beforeSend:function(){
                    lib.$submit.attr('disabled',true).text("认证中，请等待...");
                },
                success:function(data){
                    if(!data.validate == 'true') return org.ui.alert('认证失败，请重试');
                    //org.ui.alert("实名认证成功!",function(){
                    //    window.location.href = '/weixin/sub_regist_second/';
                    //});
                    //org.ui.alert("实名认证成功!",{url:'/weixin/sub_regist_second/'});
                    $('.sign-main').css('display','-webkit-box');
                },
                error:function(xhr){
                    result = JSON.parse(xhr.responseText);
                    if(result.error_number == 8){
                        //org.ui.alert(result.message,function(){
                        //   window.location.href = '/weixin/sub_list/';
                        //});
                        $('.sign-main-error').css('display','-webkit-box').find(".sign-tit").html(result.message);
                    }else{
                        return org.ui.alert(result.message);
                    }

                },
                complete:function(){
                    lib.$submit.removeAttr('disabled').text("实名认证");
                }
            })
        }
    };
    return {
        init : lib.init
    }
})(org);

org.processSecond = (function(org){
    var lib = {
        $submit: $('button[type=submit]'),
        $bank: $('select[name=bank]'),
        $bankcard: $('input[name=bankcard]'),
        $bankphone: $('input[name=bankphone]'),
        $validation: $('input[name=validation]'),
        $money: $('input[name=money]'),
        init: function(){
            lib._init_select();
            lib.form_logic();
            lib._validation();
            lib._submit();
        },
        _init_select: function(){
            lib.$bank.on("change",function(){
                var self = $(this);
                if(self.val()!=""){
                    self.removeClass("default-val");
                }else{
                    self.addClass("default-val");
                }
            });
            if(localStorage.getItem('bank')){
                var content = JSON.parse(localStorage.getItem('bank'));
                return lib.$bank.append(appendBanks(content));
            }
            org.ajax({
                type: 'POST',
                url: '/api/bank/list_new/',
                success: function(results) {
                    if(results.ret_code === 0){
                        lib.$bank.append(appendBanks(results.banks));
                        var content = JSON.stringify(results.banks);
                        window.localStorage.setItem('bank', content);
                    }else{
                        return org.ui.alert(results.message);
                    }
                },
                error:function(data){
                    console.log(data)
                }
            });

            function appendBanks(banks){
                var str = '';
                for(var bank in banks){
                    str += "<option value ="+banks[bank].gate_id+" > " + banks[bank].name + "</option>"
                }
                return str
            }

        },
        form_logic: function(){
            var _self = this;
            org.ui.focusInput({
                submit : _self.$submit,
                inputList: [
                    {target : _self.$bankcard,required : true},
                    {target : _self.$bankphone,required : true},
                    {target : _self.$validation,required : true},
                    {target : _self.$money,required : true}
                ],
                otherTarget : [{target: _self.$bank,required: true}]
            });

            org.ui.focusInput({
                submit : $('.regist-validation'),
                inputList: [
                    {target : _self.$bankcard,required : true},
                    {target : _self.$bankphone,required : true},
                    {target : _self.$money,required : true}
                ],
                otherTarget: [{target: _self.$bank,required: true}],
                submitStyle: {
                    'disabledBg': '#ccc',
                    'activeBg': '#50b143',
                }

            });

            var addClass = _self.$bank.attr('data-icon'),
                $target = $('.'+_self.$bank.attr('data-target2'));

            _self.$bank.change(function() {
                if($(this).val() == ''){
                    $target.addClass(addClass).removeClass(addClass + '-active');
                }else{
                    $target.addClass(addClass + '-active').removeClass(addClass);
                }
                _self.$bankcard.trigger('input')
            });

        },
        _validation: function(){
            var _self = this,
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/),
                $validationBtn = $('.regist-validation');

            $validationBtn.on('click', function(){
                var count = 60, intervalId ; //定时器

                if(_self.$bankcard.val().length < 10){
                    return org.ui.alert('银行卡号不正确');
                }

                if(!re.test(_self.$bankphone.val())){
                    return org.ui.alert('请填写正确手机号');
                }

                $(this).attr('disabled', 'disabled').css('background','#ccc');
                //倒计时
                var timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return $validationBtn.text( count + '秒后可重发');
                    } else {
                        clearInterval(intervalId);
                        $validationBtn.text('重新获取').removeAttr('disabled').css('background','#50b143');

                    }
                };
                org.ajax({
                    type: 'POST',
                    url: '/api/pay/deposit_new/',
                    data: {
                        card_no: _self.$bankcard.val(),
                        gate_id: _self.$bank.val(),
                        phone: _self.$bankphone.val(),
                        amount: _self.$money.val()
                    },
                    success: function(data) {
                        if(data.ret_code > 0) {
                            clearInterval(intervalId);
                            $validationBtn.text('重新获取').removeAttr('disabled').css('background','#50b143');
                            return org.ui.alert(data.message);
                        }else {
                            $("input[name='order_id']").val(data.order_id);
                            $("input[name='token']").val(data.token);
                        }
                    },
                    error:function(data){
                        clearInterval(intervalId);
                        $validationBtn.text('重新获取').removeAttr('disabled').css('background','#50b143');
                        return org.ui.alert(data);
                    }
                });
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            })
        },
        _submit: function(){
            var _self = this;

            _self.$submit.on('click',function(){
                org.ui.confirm("充值金额为" + _self.$money.val(), '确认充值', recharge);

            });

            function recharge(){
                org.ajax({
                    type: 'POST',
                    url: '/api/pay/cnp/dynnum_new/',
                    data: {
                         phone: _self.$bankphone.val(),
                         vcode: _self.$validation.val(),
                         order_id: $('input[name=order_id]').val(),
                         token: $('input[name=token]').val()
                    },
                    beforeSend:function(){
                        _self.$submit.attr('disabled', 'disabled').text('充值中...');
                    },
                    success: function(data) {
                        if(data.ret_code > 0) {
                            return org.ui.alert(data.message);
                        } else {
                           $('.sign-main').css('display','-webkit-box').find(".balance-sign").text(data.amount);
                        }
                    },
                    complete:function(){
                        _self.$submit.removeAttr('disabled').text('绑卡并充值');
                    }
                })
            }

        }
    };
    return {
        init : lib.init
    }
})(org);

//关闭页面，返回微信
function closePage(){
    if(typeof (WeixinJSBridge) != 'undefined'){
        WeixinJSBridge.call('closeWindow');
    }else{
        window.close();
    }
}

(function (org) {
    $.each($('script'), function(){//登录、注册
        var src = $(this).attr('src');
        if(src && src.indexOf(org.scriptName) > 0){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    });
    org.detail.init();//下载、微信分享

    $("#no-unbind,.back-weixin").addClass("clickOk").click(function(){
        closePage();
    });

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
    };

    var unbindf = false;
    function unbingFun(){
        unbindf = true;
        //var openid = $("#openid").val();
        org.ajax({
            type: "post",
            url: "/weixin/api/unbind/",
            //data: {"openid":openid},
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

    function btnAnimate(self,tp,k){//抽奖动画
        var arrStr = ["终于等到你还好我没放弃","人品大爆发！"];
        var errorStr = ['太可惜了，你竟然与大奖擦肩而过','天苍苍，野茫茫，中奖的希望太渺茫','你和大奖只是一根头发的距离','奖品何时有，把酒问青天？','据说心灵纯洁的人中奖几率更高'];
        var btns = tp.find(".award-item");
        var i = 0;
        var num = 0;
        var alt = $("#alt-box");
        var altAwardP = alt.find("#alt-award-p");
        var altCont = alt.find(".alt-cont");
        var altPro = alt.find("#alt-promot");
        var sleep = 60;
        function setAn(){
            btns.eq(i).addClass("awards-now").siblings(".award-item").removeClass("awards-now");
            if(i === k && num > 1){
                clearInterval(setAnimate);
                setTimeout(function(){
                    $("#page-bg").show();
                    if(k === 0){
                        altPro.text(errorStr[Math.floor(Math.random()*5)]);
                        altAwardP.html('');
                        altCont.removeClass("mt");
                    }else{
                        altPro.text(arrStr[Math.floor(Math.random()*2)]);
                        altAwardP.html('<span id="alt-award" class="alt-award">'+btns.eq(i-1).text()+'</span>已在您的账户中');
                        altCont.addClass("mt");
                    }
                    //altCont.find(".alt-btn").html('<span class="alt-award red-btns close-box">继续攒人品</span>');
                    self.removeClass("had-click");
                    alt.show();
                },sleep);
            }
            if(i >= btns.length){
                num ++;
                clearInterval(setAnimate);
                i = 0;
                setAnimate = setInterval(setAn,sleep);
            }else{
              i ++;
            }
        }
        var setAnimate = setInterval(function(){
            setAn();
        },sleep);
    }
    var awardBtn = true;
    //立即抽奖
    $("#award-btn").click(function(){
        var self = $(this);
        var isNum = goods;
        var nowNum = 0;
        var awardAction = "ENTER_WEB_PAGE";
        var altDom = $("#alt-box");
        if(awardsNum === 0){
            $("#page-bg").show();
            altDom.find("#alt-promot").text("大奖明天见，网利宝天天见。");
            altDom.find("#alt-award-p").text("您今天已经抽奖，明天再来碰运气吧");
            altDom.find(".alt-cont").addClass("mt");
            altDom.find(".alt-btn").html('<span class="alt-award red-btns close-box">知道了</span>');
            altDom.show();
            self.addClass("had-click");
            return;
        }
        if(awardBtn){
            awardBtn = false;
            self.addClass("had-click");
            if(awardsNum === 2){
                awardAction = 'GET_REWARD';
                nowNum = isAwards(isNum);
            }else{
                awardAction = 'IGNORE';
                nowNum = 0;
            }
        }else{
            return;
        }

        org.awardEvent(awardAction,function(d){ //ajax
            //console.log(d);
            $("#sub-award-num").text(d.left);
            isNum = parseFloat(d.amount);
        });
        var awards = self.parents("div.award-handle-box").siblings("div.award-btn-box");

        btnAnimate(self,awards,nowNum);//执行动画
    });
    //关闭弹层
    $("#alt-box").on("click",".close-box",function(){
        $(this).parents("#alt-box").hide();
        $("#page-bg").hide();
        awardBtn = true;
    });

    //抽奖活动 显示规则
    $("#show-alt-rule").click(function(){
        $("#sub-body-rule").show();
    });
    $("#close-this").click(function(){
        $(this).parents("#sub-body-rule").hide();
    });
})(org);

//页面加载完成 添加class
function onLoadClass(){
    var html = $("html");
    if(html.height() <= $(window).height()){
        html.addClass("sub-height");
    }else{
        html.removeClass("sub-height");
    }
}
function getCode(){//得到用户信息的二维码
    var phone = org.getQueryStringByName('phone');
    var original_id = document.getElementById("original_id").value;
    var code = document.getElementById("weixin_code").value;
    org.ajax({
        type: "GET",
        url: "/weixin/api/generate/qr_scene_ticket/",
        data: {"original_id":original_id, "code": code},//c:gh_32e9dc3fab8e, w:gh_f758af6347b6;code:微信关注渠道
        success: function (data) {
            $("#sub-code").html("<img src='"+ data.qrcode_url + "' />");
        },
        error: function(){
            window.location.href="/weixin/jump_page/?message=出错了";
        }
    });
}
function isIphone(id){
    var ipad = navigator.userAgent.match(/(iPad).*OS\s([\d_]+)/) ? true : false,
        iphone = !ipad && navigator.userAgent.match(/(iPhone\sOS)\s([\d_]+)/) ? true : false,
        ios = ipad || iphone;
    if (ios) {
      document.getElementById(id).style.display = 'block';
    }
}

function isAwards(k){//判断抽奖是第几项
    var is = 0;
    switch(k){
        case 0.2:
            is = 1;
            break;
        case 0.3:
            is = 2;
            break;
        case 0.4:
            is = 3;
            break;
        case 1:
            is = 4;
            break;
        case 1.5:
            is = 5;
            break;
        case 25:
            is = 6;
            break;
        case 2:
            is = 7;
            break;
        case 6:
            is = 8;
            break;
        case 10:
            is = 9;
            break;
        default :
            is = 0;
            break;
    }
    return is;
}

var awardsNum = 0,
    goods = '';
org.awardEvent = (function(org){ //微信抽奖
    var awardFun = function(obj, fn){
        org.ajax({
            type: "post",
            url: '/api/weixin/distribute/redpack/',
            dataType: 'json',
            data: {"action": obj,"openid": $("#openid").val()},
            success: function(data){
                fn(data);
                awardsNum = data.left;
                goods = parseFloat(data.amount);
            },
            error: function(){}
        });
    };
    return awardFun;
})(org);
