


org.mmIndex = (function(org){
    var lib = {
        $body_h : $('.maimai-check-body'),
        $submit : $('.maimai-form-btn'),
        $phone : $('input[name=phone]'),
        $codeimg : $('input[name=codeimg]'),
        $codenum : $('input[name=codenum]'),
        $sign: $('.maimai-form-sign'),
        $nbsp : $('.maimai-sign-margin'),

        init:function(){
            lib._fetchPack();
        },
        _fetchPack: function(){
            var
                _self = this,
                $domlist = [ _self.$phone, _self.$codeimg, _self.$codenum ];
            //检查手机号的回调
            var phoneback = function(){
                    var val = lib.$phone.val();
                    //手机号是否正确
                    if(lib._checkPhone(val)){
                        _self.$sign.css('height','0');  //隐藏提示
                        _self.$nbsp.css('height','.7rem');
                        lib.$phone.addClass('maimai-load'); //显示加载
                        lib.user_exists(val); //判断手机号是否已经注册
                    }else{
                        _self.$sign.css('height','1.275rem'); //显示提示
                        _self.$nbsp.css('height','0');
                        lib.$body_h.css({'height': '0'});  //隐藏验证区域
                        lib.$phone.removeAttr('data-existing');
                        lib.$phone.removeClass('maimai-load'); //隐藏加载
                    }

                    lib._canSubmit() ? lib.$submit.removeAttr('disabled'): lib.$submit.attr('disabled', 'true');
                };
            //检查图形验证码是否填写的回调
            var codeimgback = function(){
                    var val = lib.$codeimg.val();
                    if(val == ''){
                        lib.$codeimg.attr('data-post','false');
                    }else{
                        lib.$codeimg.attr('data-post','true');
                    }
                    lib._canSubmit() ? lib.$submit.removeAttr('disabled'): lib.$submit.attr('disabled', 'true');
                };
            //检查短信验证码是否填写的回调
            var codenumback = function(){
                    var val = lib.$codenum.val();
                    if(val == ''){
                        lib.$codenum.attr('data-post','false');
                    }else{
                        lib.$codenum.attr('data-post','true');
                    }

                    lib._canSubmit() ? lib.$submit.removeAttr('disabled'): lib.$submit.attr('disabled', 'true');
                };
            //三个回调的数组集合
            var callbackList = [phoneback, codeimgback, codenumback];

            //侦听三个input
            $.each($domlist, function(i, dom){
                //当空间时间大于300毫秒才执行回调，防止触发频繁
                $(dom).on('input', _self._debounce(callbackList[i],400));
            });

            //提交按钮
            _self.$submit.on('click', function(){
                phone = _self.$phone.val();

                if(_self._checkPhone(phone)){
                }else{
                  return
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
        /*
         * 判断账号接口
         */
        user_exists :function(identifier){
            var _self = this;
            //判断是否注册过
            org.ajax({
                url:'/api/user_exists/' + identifier + '/',
                success: function(data){
                    if(data.existing){
                        _self.$phone.removeClass('maimai-load').attr('data-existing','true');
                        _self.$body_h.css({'height': '0'});
                    }else{
                        _self._fetchcode();
                        _self.$phone.removeClass('maimai-load').attr('data-existing','false');
                        _self.$body_h.css({'height': '5.6rem'});
                    }
                },
                error: function (data) {
                    console.log(data)
                }
            })
        },
        /*
         * 是否可点击提交按钮
         * 当三个input全部正确可点击，
         * 当手机号是已存在用户可点击，
         */
        _canSubmit : function(){
            var
              _self = this,
              isPost = true,
              domlist=[ _self.$codeimg, _self.$codenum];

           //手机号如果存在，跳出判断 显示可点击
           if(_self.$phone.attr('data-existing') == 'true' && _self.$phone.attr('data-existing')){
                return isPost
            }

            //判断验证是否填写
            $.each(domlist, function(i, dom){
                if(dom.attr('data-post') !== 'true'){
                    return  isPost =  false
                }
            });

            //判断在验证都填写的情况下，手机号是否正确
            if(isPost){
                if(lib._checkPhone(_self.$phone.val())){
                    isPost = true
                }
            }
            return isPost
        },
        _checkPhone : function(val){
            var isRight = false,
                $sign = $('.phone-sign'),
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
            re.test($.trim(val)) ? ($sign.hide(), isRight = true) : ($sign.show(),isRight = false);
            return isRight;
        },
        _fetchcode: function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();

            $.get(captcha_refresh_url, function(res) {
                $('.check-img').attr('src', res['image_url']);
                //lib.$captcha_key.val(res['key']);
            });
        }

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