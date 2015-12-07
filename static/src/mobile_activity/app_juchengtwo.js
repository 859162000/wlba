org.jucheng = (function(org){

    var lib = {
        $body_h : $('.maimai-check-body'),
        $submit : $('.maimai-form-btn1'),
        $phone : $('input[name=phone]'),
        $codeimg : $('input[name=codeimg]'),
        $codenum : $('input[name=codenum]'),
        $sign: $('.maimai-form-sign'),
        $nbsp : $('.maimai-sign-margin'),
        $validation: $('.check-submit'),
        checkState: null,
        intervalId: null,
        $act_explain_button : $('#explain_button'),
        $explain_wrap : $('.explain_wrap'),
        init: function(){
            lib._submit();
            lib.listen();
            lib._addEvent();
            $(document.body).trigger('from:captcha');
        },
        _addEvent:function(){
            $('#explain_button').click(function(){
                $('.explain_wrap').show();
            });
            $('.explain_wrap').click(function(){
                $(this).hide();
            });
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

            //提交按钮
            _self.$submit.on('click', function(){
                if(_self.$phone.attr('data-existing') === 'true'){
                    $(document.body).trigger('from:check', [_self.checkfilter(1), false]);
                }else{
                    $(document.body).trigger('from:check', [_self.checkfilter(3), false]);
                }

                if(!lib.checkState) return

                var get_ticket_ajax = {};
                get_ticket_ajax = {
                    url: '/api/gift/owner/?promo_token=jcw',
                    type: 'POST',
                    data: {
                        phone : '',
                        address : '',
                        name : '',
                        action : 'ENTER_WEB_PAGE'
                    },
                    success: function(data){
                        if(data.award100>0){
                            $('.get_ticket_wrap').show();
                        }else{
                            $('.get_ticket_wrap1').show();
                        }
                    }
                }

                //_self.$submit.attr('disabled',true).html('领取中，请稍后...');

                    ops = {
                        url: '/api/register/?promo_token=jcw',
                        type: 'POST',
                        data: {
                            'identifier': _self.$phone.val(),
                            'validate_code': _self.$codenum.val(),
                            'IGNORE_PWD': 'true',
                            'captcha_0' :  $('input[name=codeimg_key]').val(),
                            'captcha_1' :  _self.$codeimg.val(),
                        },
                        success: function(data){
                             //console.log('11111')
                            if(data.ret_code == 0){

                                org.ajax(get_ticket_ajax);
                            }else{
                                $(document.body).trigger('from:error',[data.message, true]);
                                clearInterval(_self.intervalId);
                                $('.check-submit').text('短信验证码').removeAttr('disabled').removeClass('postValidation');
                                return $(document.body).trigger('from:captcha');
                            }
                        },
                        error: function(data){
                            //alert(data)
                        },
                        complete:function(){
                            //lib.$submit.removeAttr('disabled').html('领 取');
                        }
                    }

                org.ajax(ops);
            });
        },

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
                    //lib.$submit.removeAttr('disabled');
                    _self.$body_h.css({'height': '0'});
                    _self.$phone.attr('data-existing', true);
                    _self.$nbsp.css('height','0rem');
                    lib.$sign.css('height','1.275rem').html('该用户已注册');
                }else{
                    lib.$submit.attr('disabled',true);
                    _self.$body_h.css({'height': '5.6rem'});
                    _self.$phone.attr('data-existing', false);
                    _self.$nbsp.css('height','.7rem');
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
                    //lib.$phone.addClass('maimai-load'); //显示加载动画
                },
                success: function(data){
                    callback && callback(data);
                },
                error: function (data) {
                    //console.log(data)
                },
                complete: function(){
                    //_self.$phone.removeClass('maimai-load');
                }
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
var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ'];
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

                var host = 'https://www.wanglibao.com/',
                    shareName = '网利宝用户专享福利',
                    shareImg = host + '/static/imgs/mobile_activity/app_jucheng/300x300.jpg',
                    shareLink = host + '/activity/app_jucheng/',
                    shareMainTit = '网利宝用户专享福利',
                    shareBody = '张昊辰钢琴独奏会门票限量抢'
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg
                });
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: '网利宝用户专享福利',
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

