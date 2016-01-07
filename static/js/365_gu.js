js(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            'activityRegister': 'activityRegister'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });
    require(['jquery', 'activityRegister'],
    function($, re) {
        var popup_bg_static = false;
        re.activityRegister.activityRegisterInit({
            isNOShow: '1',
            hasCallBack: true,
            callBack: function() {
                $.ajax({
                    url: '/api/gift/owner/?promo_token=365gu',
                    type: "POST",
                    data: {
                        phone: '',
                        address: '',
                        name: '',
                        action: 'ENTER_WEB_PAGE'
                    }
                }).done(function(json) {
                    $('.get_red').show();
                    $('.register_wrap').hide();
                    popup_bg_static = true
                })
            }
        });

        $('#button,#button_get,.act_wrap .box').click(function() {
            if(popup_bg_static){
                $('.get_red,.popup_bg').show();
            }else{
                $('.register_wrap,.popup_bg').show();
            }
        });
        $('.popup_bg').click(function() {
            if (popup_bg_static == true) {
                $('.popup_bg,.get_red,.span12-omega').hide();
                $('#reg_identifier,#id_validate_code,#reg_password,#reg_password2,#id_captcha_1').val('');
                $('#aug-form-row-eroor').text('')
            }
        });
        $('.close_ico').click(function() {
            $('.popup_bg,.register_wrap,.span12-omega').hide();
            $('#reg_identifier,#id_validate_code,#reg_password,#reg_password2,#id_captcha_1').val('');
            $('#aug-form-row-eroor').text('')
        })
    })

}).call(this);