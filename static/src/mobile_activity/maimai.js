
org.mmIndex = (function(org){
    var lib = {
        $body_h : $('.maimai-check-body'),
        $submit : $('.maimai-form-btn'),
        $phone : $('input[name=phone]'),
        $codeimg : $('input[name=codeimg]'),
        $codenum : $('input[name=codenum]'),
        $sign: $('.maimai-form-sign'),
        $nbsp : $('.maimai-sign-margin'),
        $validation: $('.check-submit'),
        checkState: null,
        intervalId: null,
        init: function(){
            lib._promotoken();
            lib._submit();
            lib.listen();
            $(document.body).trigger('from:captcha');
        },
        _promotoken : function(){
            var promo_token = lib._getUrlParam("promo_token");
            if(promo_token == 'wdty518'){
                $('.maimai-rule').attr('href','/activity/maimai_rules/?promo_token=wdty518');
            }
        },
        _getUrlParam : function(name){
            var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
            var r = window.location.search.substr(1).match(reg);
            if (r!=null) return unescape(r[2]);
            return null;
        },
         _confirm: function (title, certainName, callback, callbackData) {
            if ($('.confirm-warp').length > 0) {
                $('.confirm-text').text(title);
                $('.confirm-certain').text(certainName);
                $('.confirm-warp').show();

                $('.confirm-cancel').on('click', function (e) {
                    $('.confirm-warp').hide();
                })
                $('.confirm-certain').on('click', function (e) {
                    $('.confirm-warp').hide();

                    if (callback) {
                        callbackData ? callback(callbackData) : callback();
                    }
                })
            }
        },
        checkfilter:function(num){
            var
                _self = this,
                checkAll =  [
                    { type: _self.$phone.attr('data-type'), dom: _self.$phone, message: _self.$phone.attr('data-message')},
                    { type: _self.$codeimg.attr('data-type'), dom: _self.$codeimg, message: _self.$codeimg.attr('data-message')},
                    { type: _self.$codenum.attr('data-type'), dom: _self.$codenum, message: _self.$codenum.attr('data-message')}
                ];
                checkAll.splice(num, 10)
            return checkAll

        },
        listen: function(){
            var _self = this;

            $(document).on('from:captcha', function(){
                _self._fetchcode();
            });

            $(document).on('from:validation', function(){
                _self._fetchValidation();
            });

            // arrry {checklist} 验证列表
            // bool {post} 是否验证手机号已存在
            // bool {state} 错误提醒是否显示
            // bool {other} 其他验证不参与disabled逻辑
            $(document).on('from:check', function(e, checklist, post, state, other){
                _self._check(checklist, post, state, other)
            });

            /*
             * bool {post} 是否验证手机号已存在
             * bool {other} 其他验证不参与disabled逻辑
             */
            $(document).on('from:success', function(e, post, other){
                _self._success(post, other);
            });
            /*
             * string {message} 错误提醒
             * bool {state} 错误提醒是否显示
             */
            $(document).on('from:error', function(e, message, state, other){
                _self._error(message, state, other)
            });

            var
                list = [_self.$phone, _self.$codeimg, _self.$codenum],
                checkOps = {};
            $.each(list, function(i,dom){
                dom.on('input', _self._debounce(function(){
                    checkOps = i === 0 ? { filter : 1, post: true, state: true } : { filter : 3, post: false, state: false };

                    $(document.body).trigger('from:check', [_self.checkfilter(checkOps.filter), checkOps.post, checkOps.state]);
                },400));
            });

            //刷新验证码
            $('.check-img').on('click', function() {
                $(document.body).trigger('from:captcha')
            });
            //短信验证码
            $('.check-submit').on('click',function(){
                $(document.body).trigger('from:validation');
            });
        },
        _submit: function(){
            var _self = this;

            //提交按钮22
            _self.$submit.on('click', function(){
                if(_self.$phone.attr('data-existing') === 'true'){
                    $(document.body).trigger('from:check', [_self.checkfilter(1), false]);
                }else{
                    $(document.body).trigger('from:check', [_self.checkfilter(3), false]);
                }

                if(!lib.checkState) return

                var ops = {};
                var token = $('input[name=token]').val();

                _self.$submit.attr('disabled',true).html('领取中，请稍后...');
                if(_self.$phone.attr('data-existing') === 'true'){
                    _self._alert('您已注册过网利宝！')
                }else{
                    ops = {
                        url: '/api/register/?promo_token='+token,
                        type: 'POST',
                        data: {
                            'identifier': _self.$phone.val(),
                            'validate_code': _self.$codenum.val(),
                            'IGNORE_PWD': 'true',
                            'captcha_0' :  $('input[name=codeimg_key]').val(),
                            'captcha_1' :  _self.$codeimg.val(),
                        },
                        success: function(data){
                            if(data.ret_code == 0){
                                window.location.href = '/activity/maimai_success/?state=2'
                            }else{
                                $(document.body).trigger('from:error',[data.message, true]);
                                clearInterval(_self.intervalId);
                                $('.check-submit').text('短信验证码').removeAttr('disabled').removeClass('postValidation')
                                return $(document.body).trigger('from:captcha');
                            }
                        },
                        error: function(data){
                            alert(data)
                        },
                        complete:function(){
                            lib.$submit.removeAttr('disabled').html('领 取');
                        }
                    }
                }
                org.ajax(ops);
            });
        },
        /*
         * fn 回调函数
         * delay 空闲时间
         */
        _debounce :function(fn, delay){
            var timer = null;
            return function () {
                var
                  context = this,
                  args = arguments;
                clearTimeout(timer);

                timer = setTimeout(function () {
                    fn.apply(context, args);
                }, delay);
            };
        },
        _check: function(checklist, post, state, other){

            var check = {};

            $.each(checklist, function(i,hash){
                check.checkback = lib['_check' + hash.type]($(hash.dom).val());
                check.message = hash.message;
                if(!check.checkback) return false
            });

            if(check.checkback){
                lib.checkState = true;
                $(document).trigger('from:success', [post, other]);
            }else{
                lib.checkState = false;
                $(document).trigger('from:error', [check.message, state, other] )
            }
        },
        _error: function(message, state, other){
            if(state){
                lib.$sign.css('height','1.275rem').html(message);
                lib.$nbsp.css('height','0');
            }
            if(!other) lib.$submit.attr('disabled',true);
        },
        _success: function(post, other){
            var _self = this;

            _self.$sign.css('height','0');  //隐藏提示
            _self.$nbsp.css('height','.7rem');

            // post 为ture 进行用户验证
            //post 为false 说明为展开场景,check三个按钮，按钮可点击
            if(post){
                lib.user_exists(callback);
            }else{
                if(!other) lib.$submit.removeAttr('disabled');
            }

            function callback (data){
                if(data.existing){
                    _self._confirm('您已经是我们的老用户，立即去理财！', '确定', function(){
                        window.location.href= '/weixin/list/'
                    })
                    $(document.body).trigger('from:error',['您已经是我们的老用户', true, false]);
                    _self.$body_h.css({'height': '0'});
                    _self.$phone.attr('data-existing', true);
                }else{
                    lib.$submit.attr('disabled',true);
                    _self.$body_h.css({'height': '5.6rem'});
                    _self.$phone.attr('data-existing', false);
                    $(document.body).trigger('from:check', [_self.checkfilter(3), false, false]);
                }
            }
        },
        _checkPhone : function(val){
            var isRight = false,
                $sign = $('.phone-sign'),
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
            re.test($.trim(val)) ? ($sign.hide(), isRight = true) : ($sign.show(),isRight = false);
            return isRight;
        },
        _checkVal : function(val){

            if(val == '') return false
            return true
        },
        _fetchcode: function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function(res) {
                $('.check-img').attr('src', res['image_url']);
                $('input[name=codeimg_key]').val(res['key']);
            });
        },
        _fetchValidation:function(){
            var
                _self = this,
                count = 60;  //60秒倒计时

            $(document.body).trigger('from:check', [lib.checkfilter(2), false, true, true]);

            if(!_self.checkState) return;

            $('.check-submit').attr('disabled', 'disabled').addClass('postValidation');
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
                    $('.check-submit').text('短信验证码').removeAttr('disabled').removeClass('postValidation');
                    $(document.body).trigger('from:error',[result.message, true]);
                    $(document.body).trigger('from:captcha')
                }
            });
            //倒计时
            var timerFunction = function() {
                if (count >= 1) {
                    count--;
                    return $('.check-submit').text(count + '秒后可重发');
                } else {
                    clearInterval(_self.intervalId);
                    $('.check-submit').text('重新获取').removeAttr('disabled').removeClass('postValidation')
                    return $(document.body).trigger('from:captcha');
                }
            };
            timerFunction();
            return _self.intervalId = setInterval(timerFunction, 1000);

        },
        /*
         * 判断账号接口
         */
        user_exists :function(callback){
            var _self = this;
                 phone = _self.$phone.val();
            //判断是否注册过
            org.ajax({
                url:'/api/user_exists/' + phone + '/',
                beforeSend: function(){
                    lib.$phone.addClass('maimai-load'); //显示加载动画
                },
                success: function(data){
                    callback && callback(data);
                },
                error: function (data) {
                    console.log(data)
                },
                complete: function(){
                    _self.$phone.removeClass('maimai-load');
                }
            })
        },

    }
    return {
        init : lib.init
    }
})(org);

org.mmRule = (function(org){
    var lib = {
        init: function () {
            lib._promotoken();
        },
        _promotoken: function () {
            var promo_token = lib._getUrlParam("promo_token");
            if (promo_token == 'wdty518') {
                $('.wdty').show();
            }else{
                $('.other').show();   
            }
        },
        _getUrlParam: function (name) {
            var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
            var r = window.location.search.substr(1).match(reg);
            if (r != null) return unescape(r[2]);
            return null;
        },
    }
    return {
        init : lib.init
    }
})(org);

org.success = (function(org){
    var lib = {
        init:function(){
            var
                state = org.getQueryStringByName('state')*1,
                str = null,
                val = null,
                url = null;

                if(state === 0){
                    str = '成功领取';
                    val = '1.0%加息券';
                    url = '/weixin/login/';
                }else if(state === 1){
                    str = '您已领取过奖品!';
                    val = null;
                    url = '/weixin/login/';
                }else if(state === 2){
                    str = '成功领取';
                    val = '120元红包';
                    url = '/weixin/list/';
                }
                $('.maimai-title').html(str);
                if(val){
                    $('.maimai-money').html(val);
                }
            $('.maimai-use-btn').on('click', function(){
                window.location.href = url;
            });

            var mySwiper = new Swiper('.swiper-container', {
                pagination: '.swiper-pagination-maimai',
            })
        },
    }
    return {
        init : lib.init
    }
})(org);

;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if(src){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);