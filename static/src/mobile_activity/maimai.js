


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
        $validationTime: false,  //验证码有效期控制
        checkState: null,
        init: function(){
            lib._submit();
            lib.listen();
            $(document.body).trigger('from:captcha');
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

            //图形验证码
            $(document).on('from:captcha', function(){
                _self.$validationTime = true;
                _self._fetchcode();
            });

            //短信验证码
            $(document).on('from:validation', function(){
                _self._fetchValidation();
            });
            //check 表单
            $(document).on('from:check', function(e, checklist, post){
                _self._check(checklist, post)
            });

            //表单chek 成功
            $(document).on('from:success', function(e, post){
                _self._success(post);
            });

            //表单chek 失败
            $(document).on('from:error', function(e, message){
                _self._error(message)
            });

            //当空间时间大于300毫秒才执行回调，防止触发频繁
            _self.$phone.on('input', _self._debounce(function(){
                $(document.body).trigger('from:check', [_self.checkfilter(1), true])
            },400));

            //刷新验证码
            $('.check-img').on('click', function() {
                $(document.body).trigger('from:captcha')
            });

            //获取短信验证码
            $('.check-submit').on('click',function(){
                if(!_self.$validationTime) $(document.body).trigger('from:captcha');
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

                var ops = {};
                if(_self.$phone.attr('data-existing') === 'true'){
                    ops = {
                        url: '/api/distribute/redpack/'+phone+'/?promo_token=momo',
                        type: 'post',
                        success: function(data){
                            console.log(data)
                        },
                        error: function(data){

                        }
                    }
                }else{
                    ops = {
                        url: '/api/register/',
                        type: 'POST',
                        data: {
                            'identifier': _self.$phone.val(),
                            'validate_code': _self.$codenum.val(),
                            'IGNORE_PWD': 'true',
                            'captcha_0' :  $('input[name=codeimg_key]').val(),
                            'captcha_1' :  $('input[name=codeimg]').val(),
                        },
                        success: function(data){
                            console.log(data)
                        },
                        error: function(data){

                        }
                    }
                }

                org.ajax(ops)

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
        _check: function(checklist, post){

            var check = {};

            $.each(checklist, function(i,hash){

                check.checkback = lib['_check' + hash.type]($(hash.dom).val());
                check.message = hash.message;
                if(!check.checkback) return false
            });

            if(check.checkback){
                lib.checkState = true;
                $(document).trigger('from:success', post);
            }else{
                lib.checkState = false;
                $(document).trigger('from:error', check.message)
            }
        },
        _error: function(message){
            lib.$sign.css('height','1.275rem').html(message); //显示提示
            lib.$nbsp.css('height','0');
        },
        _success: function(post){
            var _self = this;

            _self.$sign.css('height','0');  //隐藏提示
            _self.$nbsp.css('height','.7rem');

            if(post) lib.user_exists(callback);

            function callback (data){
                if(data.existing){
                    _self.$body_h.css({'height': '0'});
                    _self.$phone.attr('data-existing', true);
                }else{
                    _self.$body_h.css({'height': '5.6rem'});
                    _self.$phone.attr('data-existing', false);
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
                count = 10,  //60秒倒计时
                intervalId ; //定时器


            $(document.body).trigger('from:check', [lib.checkfilter(2), false]);

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
                    clearInterval(intervalId);
                    var result = JSON.parse(xhr.responseText);
                    $('.check-submit').text('数字验证码').removeAttr('disabled').removeClass('postValidation');
                    $(document.body).trigger('from:error',[result.message]);
                    if(xhr.status == 429) _self.$validationTime = false;
                },
                success: function(){
                    times();
                    _self.$validationTime = false;
                }
            });

            //倒计时
            function times(){
                count --;
                $('.check-submit').text(count + '秒后可重发');
                intervalId = setTimeout(times, 1000);
                if ( count <= 0 ){
                    count = 10;
                    $('.check-submit').text('重新获取').removeAttr('disabled').removeClass('postValidation');
                    //$(document.body).trigger('from:captcha');
                    clearTimeout(intervalId);
                }
            }



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

org.mmSuccess = (function(org){
    var lib = {
        init:function(){
            console.log('end')
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