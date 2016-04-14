!function (t, a) {
    "function" == typeof define && define.amd ? define(a) : "object" == typeof exports ? module.exports = a(require, exports, module) : t.CountUp = a()
}(this, function (t, a, e) {/*

 countUp.js
 (c) 2014-2015 @inorganik
 Licensed under the MIT license.

 */
    var n = function (t, a, e, n, i, r) {
        for (var o = 0, s = ["webkit", "moz", "ms", "o"], u = 0; u < s.length && !window.requestAnimationFrame; ++u)window.requestAnimationFrame = window[s[u] + "RequestAnimationFrame"], window.cancelAnimationFrame = window[s[u] + "CancelAnimationFrame"] || window[s[u] + "CancelRequestAnimationFrame"];
        window.requestAnimationFrame || (window.requestAnimationFrame = function (t, a) {
            var e = (new Date).getTime(), n = Math.max(0, 16 - (e - o)), i = window.setTimeout(function () {
                t(e + n)
            }, n);
            return o = e + n, i
        }), window.cancelAnimationFrame || (window.cancelAnimationFrame = function (t) {
            clearTimeout(t)
        }), this.options = {useEasing: !0, useGrouping: !0, separator: ",", decimal: "."};
        for (var m in r)r.hasOwnProperty(m) && (this.options[m] = r[m]);
        "" === this.options.separator && (this.options.useGrouping = !1), this.options.prefix || (this.options.prefix = ""), this.options.suffix || (this.options.suffix = ""), this.d = "string" == typeof t ? document.getElementById(t) : t, this.startVal = Number(a), this.endVal = Number(e), this.countDown = this.startVal > this.endVal, this.frameVal = this.startVal, this.decimals = Math.max(0, n || 0), this.dec = Math.pow(10, this.decimals), this.duration = 1e3 * Number(i) || 2e3;
        var l = this;
        this.version = function () {
            return "1.6.0"
        }, this.printValue = function (t) {
            var a = isNaN(t) ? "--" : l.formatNumber(t);
            "INPUT" == l.d.tagName ? this.d.value = a : "text" == l.d.tagName || "tspan" == l.d.tagName ? this.d.textContent = a : this.d.innerHTML = a
        }, this.easeOutExpo = function (t, a, e, n) {
            return e * (-Math.pow(2, -10 * t / n) + 1) * 1024 / 1023 + a
        }, this.count = function (t) {
            l.startTime || (l.startTime = t), l.timestamp = t;
            var a = t - l.startTime;
            l.remaining = l.duration - a, l.options.useEasing ? l.countDown ? l.frameVal = l.startVal - l.easeOutExpo(a, 0, l.startVal - l.endVal, l.duration) : l.frameVal = l.easeOutExpo(a, l.startVal, l.endVal - l.startVal, l.duration) : l.countDown ? l.frameVal = l.startVal - (l.startVal - l.endVal) * (a / l.duration) : l.frameVal = l.startVal + (l.endVal - l.startVal) * (a / l.duration), l.countDown ? l.frameVal = l.frameVal < l.endVal ? l.endVal : l.frameVal : l.frameVal = l.frameVal > l.endVal ? l.endVal : l.frameVal, l.frameVal = Math.round(l.frameVal * l.dec) / l.dec, l.printValue(l.frameVal), a < l.duration ? l.rAF = requestAnimationFrame(l.count) : l.callback && l.callback()
        }, this.start = function (t) {
            return l.callback = t, l.rAF = requestAnimationFrame(l.count), !1
        }, this.pauseResume = function () {
            l.paused ? (l.paused = !1, delete l.startTime, l.duration = l.remaining, l.startVal = l.frameVal, requestAnimationFrame(l.count)) : (l.paused = !0, cancelAnimationFrame(l.rAF))
        }, this.reset = function () {
            l.paused = !1, delete l.startTime, l.startVal = a, cancelAnimationFrame(l.rAF), l.printValue(l.startVal)
        }, this.update = function (t) {
            cancelAnimationFrame(l.rAF), l.paused = !1, delete l.startTime, l.startVal = l.frameVal, l.endVal = Number(t), l.countDown = l.startVal > l.endVal, l.rAF = requestAnimationFrame(l.count)
        }, this.formatNumber = function (t) {
            t = t.toFixed(l.decimals), t += "";
            var a, e, n, i;
            if (a = t.split("."), e = a[0], n = a.length > 1 ? l.options.decimal + a[1] : "", i = /(\d+)(\d{3})/, l.options.useGrouping)for (; i.test(e);)e = e.replace(i, "$1" + l.options.separator + "$2");
            return l.options.prefix + e + n + l.options.suffix
        }, l.printValue(l.startVal)
    };
    return n
});


org.ui = (function () {
    var lib = {
        _alert: function (txt, callback) {
            if (document.getElementById("alert-cont")) {
                document.getElementById("alertTxt").innerHTML = txt;
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
            } else {
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText = "position:absolute;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
                var alertFram = document.createElement("DIV");
                alertFram.id = "alert-cont";
                alertFram.style.cssText = "position:absolute; top:35%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
                strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 1.25rem .75rem;'>" + txt + "</div>";
                strHtml += " <div class='popub-footer' style='width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;'>确认</div>";
                alertFram.innerHTML = strHtml;
                document.body.appendChild(alertFram);
                document.body.appendChild(shield);

                $('.popub-footer').on('click', function () {
                    alertFram.style.display = "none";
                    shield.style.display = "none";
                    callback && callback();
                })
            }
            document.body.onselectstart = function () {
                return false;
            };
        }
    }

    return {
        alert: lib._alert,
    }
})();

var weChatShare = (function(org){
    var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
        org.ajax({
            type : 'GET',
            url : '/weixin/api/jsapi_config/',
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
                shareImg = host + '/static/imgs/mobile/weChat_logo.png',
                shareLink = $('input[name=url]').val(),
                shareMainTit = '送你300元现金豪礼，就是这么任性！',
                shareBody = '新人立领300元现金红包，专享16%超高收益，史无前例！100元起投立即去看看～戳这里>>';
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
})(org);

org.invite_index = (function (org) {
    var lib = {
        $phone: $('input[name=phone]'),
        $codeimg : $('input[name=codeimg]'),
        $codenum : $('input[name=codenum]'),
        $sign: $('.mod-form-sign'),
        $nbsp : $('.mod-sign-margin'),
        spread: $(document),
        $body_h : $('.mod-check-body'),
        $agreement: $("#agreement"),
        checkState: null,
        init: function () {
            lib._initNum(lib._animate);
            lib._registerListen();
        },
        _initNum: function (callback) {
            var $num = $('.num-space')
            $num.each(function () {
                var amount = parseInt($(this).attr('data-number')).toString(),
                    type = $(this).attr('data-type');
                $(this).append(amountGe(amount, type, lib.animate));
            })

            callback && callback();
            function amountGe(value, type) {
                var len = value.length, str = '';
                reType = type == 'man' ? '人' : '元';
                if (len > 8) {
                    str = isNode(value.substr(0, len - 8), '亿') + isNode(value.substr(-8, 4), '万');
                } else {
                    str = isNode(value.substr(0, len - 4), '万');
                }
                function isNode(substr, text) {
                    if (parseInt(substr) > 0) {
                        return " <span class='animate-num' id='animate"+substr+"'>" + parseInt(substr) + "</span> <span class='animate-text'>" + text + '</span>';
                    }
                    return '';
                }
                return str
            }
        },
        _animate: function () {
            $('.animate-num').each(function(i){
                var thisId = $(this).attr('id')
                new CountUp(thisId, 0, parseInt($(this).html()), 0, 2,{
                    useEasing : false,
                    useGrouping : false,
                }).start();
            })
        },
        _registerListen: function() {
            var _self = this;

            _self.spread.on('from:captcha', function(){
                _self._fetchcode();
            });

            _self.spread.on('from:validation', function(){
                _self._fetchValidation();
            });

            // arrry {checklist} 验证列表
            _self.spread.on('from:check', function(e, checklist, callback){
                _self._check(checklist, callback)
            });

            /*
             * bool {post} 是否验证手机号已存在
             * bool {other} 其他验证不参与disabled逻辑
             */
            _self.spread.on('from:showSign', function(e, message){
                _self._showSign(message);
            });
            /*
             * string {message} 错误提醒
             * bool {state} 错误提醒是否显示
             */
            _self.spread.on('from:hideSign', function(e){
                _self._hideSign()
            });

            //刷新验证码
            $('.check-img').on('click', function() {
                _self.spread.trigger('from:captcha')
            });
            //短信验证码
            $('.check-submit').on('click',function(){
                _self.spread.trigger('from:validation');
            });


            $("#agreement").on('click',function(){
                $(this).toggleClass('agreement');
                $(this).hasClass('agreement') ?  $(this).find('input').attr('checked','checked') : $(this).find('input').removeAttr('checked');
            })

            var $registXieyi = $('.regist-protocol-div');
            $('.xieyi-btn').on('click', function(){
                 $registXieyi.css('display','block')
                setTimeout(function(){
                    $registXieyi.css('-webkit-transform','translate3d(0, 0%, 0)')
                },30)
            })
            $('.cancel-xiyie').on('click', function(){
                $registXieyi.css('-webkit-transform','translate3d(0, 100%, 0)')
                setTimeout(function(){
                    $registXieyi.css('display','none')
                },200)
            })

            $('input[name=submit]').on('click', function(){
                if(_self.$phone.attr('data-existing') == 'true'){
                    _self.spread.trigger('from:check', [_self.checkfilter(2), existingTrueClllback]);
                }else{
                    _self.spread.trigger('from:check', [_self.checkfilter(4), existingFalseClllback]);
                }
            });

            function existingTrueClllback(data){
                if(data.checkback){
                    _self._user_exists();
                }else{
                   return  _self.spread.trigger('from:showSign',[data.message])
                }
            }

            function existingFalseClllback(data){
                if(data.checkback){
                    _self._regist_wlb();
                }else{
                    return _self.spread.trigger('from:showSign',[data.message])
                }
            }

        },
        _regist_wlb: function(){
            var _self = this;
            org.ajax({
                url: '/api/register/',
                type: 'POST',
                data: {
                    "identifier":  _self.$phone.val(),
                    "validate_code": _self.$codenum.val(),
                    "IGNORE_PWD": 'true',
                    'invite_code': $('#invite_code').val()
                },
                beforeSend: function(){
                    $('input[name=submit]').attr('disabled',true)
                },
                success:function(data){
                    var base64Native = Base64.encode(_self.$phone.val());
                    var styleBase = base64Native.substring(0,base64Native.length-1);
                    if(data.ret_code === 0 ){
                        window.location.href='/wst/'+ styleBase+'/';
                    }else if (data.ret_code === 30015){
                        window.location.href = '/wsf/'+ styleBase+'/';
                    }else{
                        return _self.spread.trigger('from:showSign',[data.message])
                    }
                },
                error: function(data){
                    org.ui.alert(data)
                },
                complete:function(){
                    $('input[name=submit]').removeAttr('disabled')
                }
            })
        },
        /*
         * 判断账号接口
         */
        _user_exists :function(callback){
            var _self = this;
                 phone = _self.$phone.val();
            //判断是否注册过
            org.ajax({
                url:'/api/user_exists/' + phone + '/',
                beforeSend: function(){
                    lib.$phone.addClass('mod-load'); //显示加载动画
                    $('input[name=submit]').attr('disabled',true)
                },
                success: function(data){
                    if(data.existing){
                        var base64Native = Base64.encode(_self.$phone.val());
                        var styleBase = base64Native.substring(0,base64Native.length-1);
                        window.location.href = '/wsf/'+ styleBase+'/';
                    }else{
                        _self.$phone.attr({'data-existing': 'false'});
                        _self.$body_h.css({'height': '6rem'});
                        _self.spread.trigger('from:captcha');
                    }
                },
                error: function (data) {
                    console.log(data)
                },
                complete: function(){
                    _self.$phone.removeClass('mod-load');
                    $('input[name=submit]').removeAttr('disabled')
                }
            })
        },
        _fetchValidation:function(){
            var
                _self = this,
                count = 60;  //60秒倒计时

           _self.spread.trigger('from:check', [_self.checkfilter(3)]);

            if(!_self.checkState) return;

            $('.check-submit').attr('disabled', 'disabled').addClass('mod-postValidation');
            org.ajax({
                url : '/api/phone_validation_code/' + _self.$phone.val() + '/',
                data: {
                    captcha_0 : $('input[name=codeimg_key]').val(),
                    captcha_1 : _self.$codeimg.val(),
                },
                type : 'POST',
                error :function(xhr){
                    clearInterval(_self.intervalId);
                    var result = JSON.parse(xhr.responseText);
                    $('.check-submit').text('短信验证码').removeAttr('disabled').removeClass('mod-postValidation');
                    $(document.body).trigger('from:showSign',[result.message]);
                }
            });
            //倒计时
            var timerFunction = function() {
                if (count >= 1) {
                    count--;
                    return $('.check-submit').text(count + '秒后可重发');
                } else {
                    clearInterval(_self.intervalId);
                    $('.check-submit').text('重新获取').removeAttr('disabled').removeClass('mod-postValidation')
                    return $(document.body).trigger('from:captcha');
                }
            };
            timerFunction();
            return _self.intervalId = setInterval(timerFunction, 1000);

        },
        checkfilter:function(num){
            var
                _self = this,
                checkAll =  [
                    { type: _self.$phone.attr('data-type'), dom: _self.$phone, message: _self.$phone.attr('data-message')},
                    { type: _self.$agreement.attr('data-type'), dom: _self.$agreement, message: _self.$agreement.attr('data-message')},
                    { type: _self.$codeimg.attr('data-type'), dom: _self.$codeimg, message: _self.$codeimg.attr('data-message')},
                    { type: _self.$codenum.attr('data-type'), dom: _self.$codenum, message: _self.$codenum.attr('data-message')}
                ];
                checkAll.splice(num, 10)
            return checkAll

        },
        _check: function(checklist , callback){

            var check = {}, _self = this;

            $.each(checklist, function(i,hash){

                check.checkback = (hash.dom)[0].tagName == 'INPUT' ? lib['_check' + hash.type]($(hash.dom).val()) : lib['_check' + hash.type]($(hash.dom));
                check.message = hash.message;
                if(!check.checkback) return false
            });
            if(check.checkback){
                _self.checkState = true;
                _self.spread.trigger('from:hideSign');
            }else{
                _self.checkState = false;
                _self.spread.trigger('from:showSign',[check.message])
            }
            callback && callback(check)
        },
        _checkPhone : function(val){
            var isRight = false,
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
            re.test($.trim(val)) ? (isRight = true) : (isRight = false);
            return isRight;
        },
        _checkVal : function(val){

            if(val == '') return false
            return true
        },
        _checkAgree: function(obj){
            if(obj.hasClass('agreement')){
                return true
            }
            return false
        },
        _fetchcode: function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function(res) {
                $('.check-img').attr('src', res['image_url']);
                $('input[name=codeimg_key]').val(res['key']);
            });
        },
        _showSign: function(message){
            lib.$sign.css('height','1.275rem').html(message);
            lib.$nbsp.css('height','0');
        },
        _hideSign: function(){
            lib.$sign.css('height','0');  //隐藏提示
            lib.$nbsp.css('height','.7rem');
        }

    }
    return {
        init: lib.init
    }
})(org);

org.invite_success = (function (org) {
    var lib = {
        init: function () {
            $('.invite-result-btn-dom').on('click', function(){
                $('.invite-mask-share').show()
            })
            $('.mask-close').on('click', function(){
                $('.invite-result-mask').css('display','none');
            })
            $('.erweima-dom').on('click', function(){
                $('.invite-result-mask').css('display','-webkit-box');
            })
            $('.invite-mask-share').on('click', function(){
                $(this).hide()
            })
        },
    }
    return {
        init: lib.init
    }
})(org);

org.invite_error = (function (org) {
    var lib = {
        init: function () {

            $('.invite-result-btn').on('click', function(){
                $('.invite-mask-share').show()
            })
            $('.invite-mask-share').on('click', function(){
                $(this).hide()
            })
        },
    }
    return {
        init: lib.init
    }
})(org);

;
(function (org) {
    $.each($('script'), function () {
        var src = $(this).attr('src');
        if (src) {
            if ($(this).attr('data-init') && org[$(this).attr('data-init')]) {
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);