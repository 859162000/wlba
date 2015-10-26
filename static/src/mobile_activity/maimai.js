


org.mmIndex = (function(org){
    var lib = {
        $body_h : $('.maimai-check-body'),
        $submit : $('.maimai-form-btn'),
        $phone : $('input[name=phone]'),
        $codeimg : $('input[name=codeimg]'),
        $codenum : $('input[name=codenum]'),
        $sign: $('.maimai-form-sign'),
        $nbsp : $('.maimai-sign-margin'),
        checkPart: [
            { type: $('input[name=phone]').attr('data-type'), dom: $('input[name=phone]'), message: $('input[name=phone]').attr('data-message')}
        ],
        checkAll: [
            { type: $('input[name=phone]').attr('data-type'), dom: $('input[name=phone]'), message: $('input[name=phone]').attr('data-message')},
            { type: $('input[name=codeimg]').attr('data-type'), dom: $('input[name=codeimg]'), message: $('input[name=codeimg]').attr('data-message')},
            { type: $('input[name=codenum]').attr('data-type'), dom: $('input[name=codenum]'), message: $('input[name=codenum]').attr('data-message')}
        ],
        init: function(){
            lib._submit();
            lib.listen();
            $(document.body).trigger('from:captcha');
        },
        listen: function(){
            var _self = this;

            $(document).on('from:captcha', function(){
                _self._fetchcode();
            });

            $(document).on('from:check', function(e, checklist){
                _self._check(checklist)
            });

            $(document).on('from:success', function(){
                _self._success();
            });

            $(document).on('from:error', function(e, message){
                _self._error(message)
            });

            //当空间时间大于300毫秒才执行回调，防止触发频繁
            _self.$phone.on('input', _self._debounce(function(){
                $(document.body).trigger('from:check', [_self.checkPart])
            },400));
        },
        _submit: function(){
            var _self = this;

            //提交按钮
            _self.$submit.on('click', function(){
                if(_self.$phone.attr('data-existing') === 'true'){
                    $(document.body).trigger('from:check', [_self.checkPart]);
                }else{
                    $(document.body).trigger('from:check', [_self.checkAll]);
                }


              //$(this).addClass('btn-activity')
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
        _check: function(checklist){

            var check = {};

            $.each(checklist, function(i,hash){

                check.checkback = lib['_check' + hash.type]($(hash.dom).val());
                check.message = hash.message;
                if(!check.checkback) return false
            });

            if(check.checkback){
                $(document).trigger('from:success');
            }else{
                $(document).trigger('from:error', check.message)
            }
        },

        _error: function(message){
            lib.$sign.css('height','1.275rem').html(message); //显示提示
            lib.$nbsp.css('height','0');
        },

        _success: function(){
            var _self = this;

            _self.$sign.css('height','0');  //隐藏提示
            _self.$nbsp.css('height','.7rem');

            lib.user_exists(callback);

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
                $('input[name=captcha_key]').val(res['key']);
            });
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