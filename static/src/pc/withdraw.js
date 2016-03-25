(function () {

    require(['jquery', 'tools', 'jquery.validate', './model/debounce', 'csrf'], function ($, tool, validate, debounce) {
        $.validator.addMethod("balance", function (value, element) {
            var balance = $(element).attr('data-balance')
            return (value - balance).toFixed(2) <= 0
        });
        $.validator.addMethod("money", function (value, element) {
            var re = /^\d+(\.\d{0,2})?$/
            return re.test
            value
        });
        $.validator.addMethod("huge", function (value, element) {
            return value <= max_amount;
        });
        $.validator.addMethod("small", function (value, element) {
            var balance;
            balance = $(element).attr('data-balance');
            if (value <= 0) {
                return false;
            }
            if (balance - value === 0) {
                return true;
            } else if (value >= min_amount) {
                return true;
            }
            return false;
        });


        var $amount = $('input[name=amount]');
        var $fee = $('input[name=fee]');
        var margin = $('.withdraw-margin').data('margin');

        $('.fees-alert').on('click', function () {
            $(this).modal()
        })

        $('.cash-amount-all').on('click', function () {
            $amount.trigger('focus').val(margin)
        });

        $amount.on('input', debounce(function () {
            checkInput($(this))
        }, 300));

        var max_amount = parseInt($fee.attr('data-max_amount')),
            min_amount = parseInt($fee.attr('data-min_amount'));

        $('#withdraw-form').validate({
            rules: {
                amount: {
                    required: true,
                    money: true,
                    balance: false,
                    huge: false,
                    small: false,
                },
                validate_code: {
                    required: true
                },
                captcha_1: {
                    required: true,
                    minlength: 1
                },
                trade_pwd: {
                    required: true
                }
            },
            messages: {
                amount: {
                    required: '请输入金额',
                    money: '请输入正确的金额格式',
                    balance: '余额不足',
                    huge: '单笔提现金额不能超过' + max_amount + '万元',
                    small: '最低提现金额 ' + min_amount + ' 元起。如果余额低于 ' + min_amount + ' 元，请一次性取完。'
                },
                validate_code: {
                    required: '请输入验证码'
                },
                captcha_1: {
                    required: '不能为空',
                    minlength: $.format("验证码至少输入1位")
                },
                trade_pwd: {
                    required: '请输入交易密码'
                }
            },
            errorPlacement: function (error, element) {
                return error.appendTo($(element).parents('td').children('.form-row-error'));
            },
            submitHandler: function (form) {

            }
        })


        var checkInput = function (target) {
            var amount = target.val();
            var cardID = target.data('card-id');

            $.post("/api/fee/", { card_id: cardID, amount: amount})
                .done(function (xhr) {
                    var strs;
                    if (xhr.ret_code > 0) {
                        target.parents('td').find('.form-row-error').html(xhr.message);
                    } else {
                        if ((xhr.fee === 0) && (xhr.management_fee === 0 || xhr.management_fee === '0')) {
                            strs = 0;
                        } else if (xhr.fee !== 0 && (xhr.management_fee === 0 || xhr.management_fee === '0')) {
                            strs = xhr.fee;
                        } else {
                            strs = xhr.fee + '+' + xhr.management_fee;
                        }
                        $('#poundage').html(parseFloat(strs));
                        return $('#actual-amount').text(xhr.actual_amount);
                    }
                });
        };

    });

}).call(this);