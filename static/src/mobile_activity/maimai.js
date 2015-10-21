


org.mmIndex = (function(org){
    var lib = {
        init:function(){
            lib._fetchPack();
        },
        _fetchPack: function(){
            var
                $submit  = $('.maimai-form-btn'),
                $phoneVal = $('input[name=phone]'),
                $sign =  $('.maimai-form-sign'),
                $nbsp = $('.maimai-sign-margin'),
                scrollTimer = null;

            //listen input
            $phoneVal.on('input',function(){
                var _ = $(this);
                if (scrollTimer) {
                    clearTimeout(scrollTimer)
                }
                scrollTimer = setTimeout(function(){
                    var phone = _.val();
                    if(lib._checkPhone(phone)){
                        _.addClass('maimai-load');
                        lib.user_exists(phone)
                    }else{
                        _.removeClass('maimai-load');
                    }

                }, 350);
            });

            $submit.on('click', function(){
                phone = $phoneVal.val();

                if(lib._checkPhone(phone)){
                  $sign.hide();
                  $nbsp.show();
                }else{
                  $sign.show();
                  $nbsp.hide();
                  return
                }
              $(this).addClass('btn-activity')
            });

        },
        user_exists :function(identifier){
            org.ajax({
                url:'/api/user_exists/' + identifier + '/',
                success: function(data){
                    console.log(data)
                    if(data.existing){
                        console.log(data.existing)
                        $('.maimai-form').removeAttr('disabled');
                    }
                },
                error: function (data) {
                    console.log(data)
                }
            })
        },

        _checkPhone : function(val){
            var isRight = false,
                $sign = $('.phone-sign'),
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
            re.test($.trim(val)) ? ($sign.hide(), isRight = true) : ($sign.show(),isRight = false);
            return isRight;
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