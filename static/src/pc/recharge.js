(function () {

    require(['jquery', 'tools', 'jquery.validate', 'csrf'], function ($, tool) {
        $('.recharge-bank-limit').on('click', function () {
            $(this).modal()
        })

        $('.racharge-bank-list li').on('click', function () {
            $(this).addClass('active').siblings().removeClass('active')
            $('#gate_id').val($(this).attr('data-gate-id'));
        })

        $("input[name=amount]").blur(function () {
            var value = $(this).val();
            if (value) {
                if (parseFloat(value).toFixed(2) === "NaN") {
                    return $(this).val("");
                } else {
                    return $(this).val(parseFloat(value).toFixed(2));
                }
            }
        });

        $("input[name=amount]").click(function (e) {
            return userStatus();
        });

        $.validator.addMethod('morethan100', function (value, element) {
            return Number(value) >= 100;
        }, '充值金额100元起');


        $("#payform").validate({
            ignore: "",
            rules: {
                amount: {
                    required: true,
                    morethan100: true
                },
                gate_id: {
                    required: true
                }
            },
            messages: {
                amount: {
                    required: '不能为空'
                },
                gate_id: {
                    required: '请选择银行'
                }
            },
            errorPlacement: function (error, element) {
                return error.appendTo($('.form-row-error'));
            },
        });

        var userStatus = function () {
            if ($('#id-is-valid').attr('data-type') === 'qiye') {
                if ($('#id-is-valid').val() === 'False') {
                    $.get( '/qiye/profile/exists/')
                        .done(function (data) {
                            if (data.ret_code === 10000) {
                                return $.get('/qiye/profile/get/')
                                           .done(function (data) {
                                               if (data.data.status !== '审核通过') {
                                                   rechargeAlert('/qiye/profile/edit/');
                                               }
                                           });
                            }else{
                                rechargeAlert('/qiye/info/');
                            }
                        })
                        .fail(function (data) {
                            rechargeAlert('/accounts/id_verify/')
                        });
                }

            }else{
                if ($('#id-is-valid').val() === 'False') rechargeAlert('/accounts/id_verify/')
            }
        };
        userStatus()

        function rechargeAlert(url){
            tool.modalAlert({
                title: '温馨提示',
                msg: '为保证您的资金安全，请先进行实名认证',
                btnText: "去实名认证",
                callback_ok: function(){
                    window.location.href= url;
                }
            })
        }
    });

}).call(this);