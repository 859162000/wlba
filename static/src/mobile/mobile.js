
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
            dom.on('input', function(e) {
                var earning, earning_element, earning_elements, fee_earning, fee_element, fee_elements;
                var target = $(e.target),
                    existing = parseFloat(target.attr('data-existing')),
                    period = target.attr('data-period'),
                    rate = target.attr('data-rate')/100,
                    pay_method = target.attr('data-paymethod');
                    activity_rate = target.attr('activity-rate')/100;
                    amount = parseFloat(target.val()) || 0;

                if (amount > target.attr('data-max')) {
                    amount = target.attr('data-max');
                    target.val(amount);
                }
                amount = parseFloat(existing) + parseFloat(amount);
                earning = calculate(amount, rate, period, pay_method);
                fee_earning = calculate(amount, activity_rate, period, pay_method);

                if (earning < 0) {
                    earning = 0;
                }
                earning_elements = (target.attr('data-target')).split(',');
                fee_elements = (target.attr('fee-target')).split(',');

                for (var i = 0; i < earning_elements.length; i ++) {
                    earning_element = earning_elements[i];
                    if (earning) {
                        earning += fee_earning;
                        $(earning_element).text(earning.toFixed(2));
                    } else {
                        $(earning_element).text("0.00");
                    }
                }
                for (var j = 0; j < fee_elements.length;  j++) {
                    fee_element = fee_elements[j];
                    if (fee_earning) {
                       $(fee_element).text(fee_earning);
                    } else {
                        $(fee_element).text("0.00");
                    }
                }
                callback && callback(target);
            });
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
                })

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


org.login = (function(org){
    var lib = {
        $captcha_img : $('#captcha'),
        $captcha_key : $('input[name=captcha_0]'),
        init:function(){
            lib._captcha_refresh();
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
                    {target: $('input[name=captcha_1]'), required : true},
                ],
            });

            //刷新验证码
            lib.$captcha_img.on('click', function() {
                lib._captcha_refresh();
            });
            $submit.on('click', function() {
                var data = {
                    'identifier': $.trim($form.find('input[name=identifier]').val()),
                    'password': $.trim($form.find('input[name=password]').val()),
                    'captcha_0': $.trim($form.find('input[name=captcha_0]').val()),
                    'captcha_1': $.trim($form.find('input[name=captcha_1]').val()),
                    'openid': $.trim($form.find('input[name=openid]').val())
                }
                org.ajax({
                    'type': 'post',
                    'url': $form.attr('action'),
                    'data': data,
                    beforeSend: function (xhr) {
                        $submit.attr('disabled', true).text('登录中..');
                    },
                    success: function(res) {
                        var next = org.getQueryStringByName('next');
                        if (next) {
                            window.location.href = decodeURIComponent(decodeURIComponent(next));;
                        }else{
                            window.location.href = '/weixin/account/';
                        }
                    },
                    error: function(res) {
                        if (res['status'] == 403) {
                            org.ui.showSign('请勿重复提交')
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
        init:function(){
            lib._checkFrom()
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
            })
            //关闭协议
            $cancelXiyi.on('click',function(){
                $protocolDiv.css('top','100%');
                setTimeout(function(){
                    $protocolDiv.css('display','none');
                },200)
            })
        },
        _checkFrom:function(){
            var $submit = $('button[type=submit]'),
                $identifier = $('input[name=identifier]'),
                $password = $('input[name=password]'),
                $validation =  $('input[name=validation]'),
                $invitation = $('input[name=invitation]'),
                $agreement = $('input[name=agreement]');

            org.ui.focusInput({
                submit : $submit,
                inputList: [
                    {target : $identifier,  required:true},
                    {target :$password,required : true},
                    {target: $validation,required : true},
                    {target: $invitation, required: false}
                ],
                otherTarget : [{target: $agreement,required: true}]
            });
            $("#agreement").on('click',function(){
                $(this).toggleClass('agreement');
                $(this).hasClass('agreement') ?  $(this).find('input').attr('checked','checked') : $(this).find('input').removeAttr('checked');
                $identifier.trigger('input')
            })

            //验证码
            $('.request-check').on('click',function(){
                var phoneNumber = $identifier.val(),
                    $that = $(this), //保存指针
                    count = 180,  //180秒倒计时
                    intervalId ; //定时器

                if(!check['identifier'](phoneNumber, 'phone')) return //号码不符合退出
                $that.attr('disabled', 'disabled').addClass('regist-alreay-request');
                org.ajax({
                    url : '/api/phone_validation_code/register/' + phoneNumber + '/',
                    type : 'POST',
                    error :function(xhr){
                        clearInterval(intervalId);
                        var result = JSON.parse(xhr.responseText);
                        org.ui.showSign(result.message);
                        $that.text('获取验证码').removeAttr('disabled').removeClass('regist-alreay-request');
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
                        return
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

            $submit.on('click',function(){
                isSubmit =  true;
                //校验主函数
                $.each(checkList, function(){
                    var value = $(this).val(), checkTarget = $(this).attr('name');
                    if(!check[checkTarget](value)){
                        return isSubmit = false
                    }
                })

                if(!isSubmit) return false
                var tid = org.getQueryStringByName('tid');
                var token = $invitation.val() === '' ?  $('input[name=token]').val() : $invitation.val();
                org.ajax({
                    url: '/api/register/',
                    type: 'POST',
                    data: {
                            'identifier':       $identifier.val(),
                            'password':         $password.val(),
                            'validate_code':    $validation.val(),
                            'invite_code':      token,
                            'tid' : tid,
                    },
                    beforeSend: function() {
                        $submit.text('注册中,请稍等...');
                    },
                    success:function(data){
                        if(data.ret_code === 0){
                            window.location.href = '/weixin/regist/succees/';
                        }else if(data.ret_code > 0){
                            org.ui.showSign(data.message)
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

org.list = (function(org){
    var lib = {
        windowHeight : $(window).height(),
        canGetPage : true, //防止多次请求
        scale : 0.8, //页面滚到百分70的时候请求
        pageSize: 10, //每次请求的个数
        page: 2, //从第二页开始
        init :function(){
            lib._swiper();
            lib._scrollListen();
        },
        _swiper:function(){
            var autoplay = 5000, //焦点图切换时间
                loop = true,  //是否无缝滚动
                $swiperSlide = $('.swiper-slide');

            if($swiperSlide.length/2 < 1){
                autoplay= 0;
                loop = false;
            }
            var myswiper = new Swiper('.swiper-container', {
                pagination: '.swiper-pagination',
                loop: loop,
                lazyLoading: true,
                autoplay: autoplay,
                autoplayDisableOnInteraction: true,

            });
        },
        _scrollListen:function(){
            $(document).scroll(function(){
                if(document.body.scrollTop / (document.body.clientHeight -lib.windowHeight ) >= lib.scale){
                    lib.canGetPage && lib._getNextPage();
                }
            });
        },
        _getNextPage :function(){
            org.ajax({
                type: 'GET',
                url: '/api/p2ps/wx/',
                data: {page: lib.page, 'pagesize': lib.pageSize},
                beforeSend:function(){
                    lib.canGetPage =false
                },
                success: function(data){
                   $('#list-body').append(data.html_data);
                    lib.page++;
                    lib.canGetPage = true;
                },
                error: function(){
                    org.ui.alert('Ajax error!')
                }
            })
        }

    };
    return {
        init : lib.init
    }
})(org);

org.detail = (function(org){
    var lib ={
        weiURL: '/weixin/api/jsapi_config/',
        countDown: $('#countDown'),
        init :function(){
            lib._tab();
            lib._animate();
            lib._share();
            lib.countDown.length > 0 && lib._countDown(lib.countDown)
        },
        /*
        * 页面动画
         */
        _animate:function(){
            $(function(){
                var $progress = $('.progress-percent')
                $payalert = $('.new-pay');
                setTimeout(function(){
                    var percent = parseFloat($progress.attr('data-percent'));
                    if(percent == 100){
                        $progress.css('margin-top','-10%');
                    }else{
                        $progress.css('margin-top', (100 - percent) + '%');
                    }
                    setTimeout(function(){
                        $progress.addClass('progress-bolang')
                    },1000)
                },300)
            })
        },
        /*
        * 公司信息tab
         */
        _tab:function(){
            $('.toggleTab').on('click',function(){
                $(this).siblings().toggle();
                $(this).find('span').toggleClass('icon-rotate');
            })
        },
        /*
        * 微信分享
         */
        _share: function(){
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
                var $productName = $('.product-name'),
                    $earningRate = $('.profit-txt'),
                    $period = $('.time-txt');

                var host = 'https://www.wanglibao.com',
                    shareName = $productName.attr('data-name'),
                    shareImg = host + '/static/imgs/mobile/share_logo.png',
                    shareLink = host + '/weixin/detail/'+$productName.attr('data-productID'),
                    shareMainTit = '我在网利宝发现一个不错的投资标的，快来看看吧',
                    shareBody = shareName + ',年收益' + $earningRate.attr('data-earn') + '%,期限' + $period.attr('data-period');
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg
                });
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: shareMainTit,
                    link : shareLink,
                    imgUrl: shareImg
                })
                //分享给QQ
                org.onMenuShareQQ({
                    title: shareMainTit,
                    desc: shareBody,
                    link : shareLink,
                    imgUrl: shareImg
                })
            })
        },
        /*
        * 倒计时
         */
        _countDown:function(target){
            var endTimeList = target.attr('data-left').replace(/-/g,'/');
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
                    m < 10 ? m = '0' + m: '';
                    s < 10 ? s = '0' + s: '';
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
            lib._calculate();
            lib._buy();
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
                redPackVal = parseFloat(lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex).attr('data-amount'))
                inputAmount  =parseInt(lib.amountInout.val()), //输入框金额
                redPackAmount = redPack.attr("data-amount"), //红包金额
                redPackMethod = redPack.attr("data-method"), //红包类型
                redPackInvestamount = parseInt(redPack.attr("data-investamount")),//红包门槛
                redPackHighest_amount = parseInt(redPack.attr("data-highest_amount")),//红包最高抵扣（百分比红包才有）
                repPackDikou = 0,
                senderAmount = 0; //实际支付金额;
            lib.redPackAmountNew = 0 ;
            if(redPackVal){ //如果选择了红包
                console.log(inputAmount)
                if(!inputAmount){
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    lib.$redpackSign.hide();//红包直抵提示
                    return
                }
                if(inputAmount < redPackInvestamount){
                    lib.$redpackSign.hide();//红包直抵提示
                    lib.$redpackForAmount.hide();//请输入投资金额
                    return $(".redpack-investamount").show();//未达到红包使用门槛
                }else{
                    if(redPackMethod == '*'){ //百分比红包
                        //如果反回来的百分比需要除于100 就把下面if改成if (inputAmount * redPackAmount/100 > redPackHighest_amount)
                        if(inputAmount * redPackAmount >= redPackHighest_amount){//是否超过最高抵扣
                           repPackDikou = redPackHighest_amount;
                        }else{//没有超过最高抵扣
                            repPackDikou = inputAmount * redPackAmount;
                        }
                    }else{  //直抵红包
                        repPackDikou = parseInt(redPackAmount);
                    }
                    senderAmount = inputAmount - repPackDikou;
                    lib.redPackAmountNew = repPackDikou;
                    lib.showredPackAmount.text(repPackDikou);//红包抵扣金额
                    lib.showAmount.text(senderAmount);//实际支付金额
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    lib.$redpackSign.show();//红包直抵提示
                }
            }else{
                lib.$redpackSign.hide();//红包直抵提示
            }
            lib.$redpackForAmount.hide();//请输入投资金额

        },
        _buy:function(){
            var $buyButton = $('.snap-up'),
                $redpack = $("#gifts-package"), redpackAmount,
                reg =/^\d+(\.\d+)?$/;
            //红包select事件
            $redpack.on("change",function(){
                if($(this).val() != ''){
                    lib.amountInout.val() == '' ? $('.redpack-for-amount').show() : lib._setRedpack();
                }else{
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    lib.$redpackSign.hide();
                }
            });

            $buyButton.on('click',function(){
                var $buySufficient = $('.buy-sufficient'),
                    balance = parseFloat($("#balance").attr("data-value")),
                    amount = $('.amount').val() *1,
                    productID = $(".invest-one").attr('data-protuctid'),
                    redPackAmount = 0;
                if(amount){
                    if(amount % 100 !== 0) return org.ui.alert('请输入100的倍数金额');
                    if(amount > balance)  return $buySufficient.show();
                }else{
                     return org.ui.alert('请输入正确的金额');
                }
                var redpackValue = $redpack[0].options[$redpack[0].options.selectedIndex].value;
                if(!redpackValue || redpackValue == ''){
                    redpackValue = null;
                }else{
                    redPackAmount = parseInt(lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex).attr('data-amount'));
                    redPackAmount ? "" : redPackAmount = 0;
                }
                if(lib.isBuy){
                   if(confirm("购买金额为" + amount)){
                        org.ajax({
                            type: 'POST',
                            url: '/api/p2p/purchase/',
                            data: {product: productID, amount: amount, redpack: redpackValue},
                            beforeSend:function(){
                                $buyButton.text("抢购中...");
                                lib.isBuy = false;
                            },
                            success: function(data){
                               if(data.data){
                                   $('.balance-sign').text(balance - data.data + lib.redPackAmountNew);
                                   $(".sign-main").css("display","-webkit-box");
                               }
                            },
                            error: function(xhr){
                                var  result;
                                result = JSON.parse(xhr.responseText);
                                if(xhr.status === 400){
                                    if (result.error_number === 1) {
                                        org.ui.alert("登录超时，请重新登录！",function(){
                                            return window.location.href= '/weixin/login/?next=/weixin/view/buy/'+productID+'/';
                                        });
                                    } else if (result.error_number === 2) {
                                        return org.ui.alert('必须实名认证！');
                                    } else if (result.error_number === 4 && result.message === "余额不足") {
                                        $(".buy-sufficient").show();
                                        return;
                                    }else{
                                        return org.ui.alert(result.message);
                                    }
                                }else if(xhr.status === 403){
                                    if (result.detail) {
                                        org.ui.alert("登录超时，请重新登录！",function(){
                                            return window.location.href = '/weixin/login/?next=/weixin/view/buy/' + productID + '/';
                                        });

                                    }
                                }
                            },
                            complete:function(){
                               $buyButton.text("确定抢购");
                                lib.isBuy = true;
                            }
                        })
                   }
                }else{
                    org.ui.alert("购买中，请稍后")
                }
            })
        }
    }
    return {
        init : lib.init
    }
})(org);

org.calculator=(function(org){
    var lib = {
        init :function(){
            org.calculate($('input[data-role=p2p-calculator]'))
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
                    window.location.href = '/weixin/view/buy/' + productId + '/?amount='+ amount + '&amount_profit=' + amount_profit;
                }
            })
        }

    }
    return {
        init : lib.init
    }
})(org);

org.recharge=(function(org){
    var lib = {
        canRecharge: true,
        init :function(){
            lib._getBankCardList();
            lib._rechargeStepFirst();
            lib._initBankNav();
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
                                $cardHave.css("opacity",0)
                                $cardNone.show();
                                setTimeout(function(){
                                    $cardNone.css("opacity",1)
                                },50)
                            },50)
                        })
                        break;
                    case 'bank-card':
                        $('.recharge-select-bank').css('display','-webkit-box');
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
                            },50)
                        }
                    }
                }
            })
            $(".bank-txt-right").on('click',function(){
                    $(".bank-list-nav").css("-webkit-transform","translate3d(0,0,0)");
            })
        },
        /*
        *  初始化默认银行卡，没有默认银行卡，现在为第一个，回调函数为银行卡列表
         */
        _initCard:function(data, callback){
            $("#card-val").val(data[0]['storable_no'].slice(0,6) + '********'+ data[0]['storable_no'].slice(-4)).attr('data-storable', data[0]['storable_no']);
            $(".bank-txt-name").text(data[0]['bank_name']);
            callback && callback();
        },
        /*
        * 银行卡列表
         */
        _cradStyle:function(cardList){
            var str = '';
            for(var card in cardList){
                str += "<div class= 'select-bank-list' data-storable="+cardList[card].storable_no+">";
                str += "<div class='bank-cont'>";
                str += "<p class='bank-name-alert'>" + cardList[card].bank_name + "</p>";
                str += "<p>尾号 " + cardList[card].storable_no.slice(-4) + "</p>";
                str += "<p>限额 200000</p>";
                str += "</div>";
                str += "<div class='bank-type'>储蓄卡</div>";
                str += "</div>";
            }
            $(".select-bank-body").append(str);

            $('.select-bank-list').on('click',function(event){
                var that = this;
                $("#card-val").val($(that).attr("data-storable").slice(0,6) + '********'+ $(that).attr("data-storable").slice(-4)).attr('data-storable', $(that).attr("data-storable"));
                $(".bank-txt-name").text($(this).find(".bank-name-alert").text());
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
                $firstBtn = $('#firstBtn'),
                $secondBtn = $('#secondBtn');

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
                if(amount > maxamount){
                     return org.ui.alert('最高充值'+ maxamount +'元！')
                }
                if(lib.canRecharge){
                    confirm("充值金额为"+amount) && lib._rechargeSingleStep(card_no,amount);
                }else{
                    return org.ui.alert('充值中，请稍后');
                }

            });
        },
        /*
        * 快捷充值接口业务
         */
        _rechargeSingleStep: function(card_no, amount) {
            org.ajax({
                type: 'POST',
                url: '/api/pay/deposit/',
                data: {card_no: card_no, amount: amount},
                beforeSend:function(){
                    lib.canRecharge = false;
                    $('#secondBtn').text("充值中..");
                },
                success: function(data) {
                    if(data.ret_code > 0) {
                        return org.ui.alert(data.message);
                    } else {
                         $('.sign-main').css('display','-webkit-box').find(".balance-sign").text(data.amount);
                    }
                },
                error:function(data){
                    if(data.status == 403){
                        org.ui.alert('登录超时，请重新登录！');
                    }
                },
                complete:function(){
                    $('#secondBtn').text("充值");
                    lib.canRecharge = true;
                }
            })
        }
    }
    return {
        init : lib.init
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
                        return
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
                })
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
                    if(confirm("充值金额为" + amount)){
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
    }
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
                })
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
                        org.ui.alert("实名认证成功!",function(){
                           return window.location.href = '/weixin/security/';
                        });
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
                }

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
    }
    return {
        init : lib.init
    }
})(org);

;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if(src && src.indexOf(org.scriptName) > 0){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);
