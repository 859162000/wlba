(function () {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            'activityRegister': 'activityRegister'
        }, shim: {'jquery.modal': ['jquery']}
    });
    require(['jquery', 'activityRegister'], function ($, re) {
        var award100;
        re.activityRegister.activityRegisterInit({
            registerTitle: '限时限量，满额直送',
            isNOShow: '1',
            hasCallBack: true,
            callBack: function () {
                $.ajax({
                    url: '/api/gift/owner/?promo_token=jcw',
                    type: "POST",
                    data: {phone: '', address: '', name: '', action: 'ENTER_WEB_PAGE'}
                }).done(function (json) {
                     award100 = json.award100
                    if(json.award100>0){
                       $('.get_ticket').show();
                    }else{
                       $('.get_ticket1').show();
                    }

                    $('.register_wrap').hide();
                    popup_bg_static = true
                })
            }
        });
        var has_ticket;
        var is_user;
        var popup_bg_static = false;
        if ($('#ganjiwang-welcome').index() != 0) {
            is_user = 0
        } else {
            is_user = 1;
            $.ajax({
                url: '/api/gift/owner/?promo_token=jcw',
                type: "POST",
                data: {'action': 'HAS_TICKET'}
            }).done(function (json) {
                has_ticket = json.has_ticket

            })
        }
        $('#button').click(function () {
            if (has_ticket) {
                $('.register_wrap').show()
            } else {
                if (is_user == 0) {
                    $('.register_wrap').show()
                } else {
                    if(award100>=0){
                        $('.get_ticket').show()
                    }else{
                        $('.get_ticket1').show()
                    }
                    popup_bg_static = true
                }
            }
            if (popup_bg_static) {
                $('.register_wrap').hide();
                if(award100>=0){
                    $('.get_ticket').show()
                }else{
                    $('.get_ticket1').show()
                }

            }
            $('.popup_bg').show()
        });
        $('.popup_bg').click(function () {
            if (popup_bg_static == true) {
                $('.popup_bg,.get_ticket,.get_ticket1,.span12-omega').hide();
                $('#reg_identifier,#id_validate_code,#reg_password,#reg_password2,#id_captcha_1').val('');
                $('#aug-form-row-eroor').text('')
            }
        });
        $('.close_ico').click(function () {
            $('.popup_bg,.register_wrap,.get_ticket1,.span12-omega').hide();
            $('#reg_identifier,#id_validate_code,#reg_password,#reg_password2,#id_captcha_1').val('');
            $('#aug-form-row-eroor').text('')
        })
    })
}).call(this);