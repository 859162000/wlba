(function () {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            'activityRegister': 'activityRegister'
        }, shim: {'jquery.modal': ['jquery']}
    });
    require(['jquery', 'activityRegister'], function ($, re) {
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
                    $('span.shi').text(json.award80);
                    $('span.bai').text(json.award100);
                    $('.get_ticket').show();
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
                    $('.get_ticket').show();
                    popup_bg_static = true
                }
            }
            if (popup_bg_static) {
                $('.register_wrap').hide();
                $('.get_ticket').show()
            }
            $('.popup_bg').show()
        });
        $('.popup_bg').click(function () {
            if (popup_bg_static == true) {
                $('.popup_bg,.get_ticket,.span12-omega').hide();
                $('#reg_identifier,#id_validate_code,#reg_password,#reg_password2,#id_captcha_1').val('');
                $('#aug-form-row-eroor').text('')
            }
        });
        $('.close_ico').click(function () {
            $('.popup_bg,.register_wrap,.span12-omega').hide();
            $('#reg_identifier,#id_validate_code,#reg_password,#reg_password2,#id_captcha_1').val('');
            $('#aug-form-row-eroor').text('')
        })
    })
}).call(this);