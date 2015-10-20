


org.mmIndex = (function(org){
    var lib = {
        init:function(){
            lib._fetchPack();
        },
        _fetchPack: function(){
            var
                $submit  = $('.maimai-form-btn'),
                phoneVal = $('input[name=phone]'),
                $sign =  $('.maimai-form-sign'),
                $nbsp = $('.maimai-sign-margin');

            $submit.on('click', function(){
                phone = phoneVal.val();

                if(lib._checkPhone(phone)){
                  $sign.hide();
                  $nbsp.show();
                }else{
                  $sign.show();
                  $nbsp.hide();
                  return
                }
              //$(this).addClass('btn-activity')
            });

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