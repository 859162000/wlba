(function () {

    require(['jquery', './model/message.validation', 'jquery.validate', './model/debounce', 'tools'], function ($, Message, validate, debounce, tool) {


        var
            $amount = $('input[name=amount]'),
            $fee = $('input[name=fee]'),
            margin = $('.withdraw-margin').data('margin'),
            max_amount = parseInt($fee.attr('data-max_amount')),
            min_amount = parseInt($fee.attr('data-min_amount')),
            $validate_code = $('input[name=validate_code]'),
            $trade_pwd = $('input[name=trade_pwd]'),
            $Message = $('.cash-phone-but'),
            $captcha_0 = $('input[name=captcha_0]'),
            $captcha_1 = $('input[name=captcha_1]'),
            $voice_message_target = $(".voice-validate");

        //收费说明
        $('.fees-alert').on('click', function () {
            $(this).modal()
        })

        //提现全部
        $('.cash-amount-all').on('click', function () {
            $amount.trigger('focus').val(margin)
            $amount.trigger('input')
        });

        //提现手续费计算
        $amount.on('input', debounce(function () {
            checkInput($(this))
        }, 300));

        //图片验证码刷新
        $('.captcha-imgs').on('click', function () {
            refreshCode()
        })

        //短信验证码初始化

        var message = new Message({
            target: $Message,
            doneCallback: function () {
                $voice_message_target.hide()
            },
            failCallback: function () {
                $captcha_1.trigger('focus').val('');
                refreshCode();
            },
            timerEndCallback: function () {
                $captcha_1.trigger('focus').val('');
                refreshCode();
                $voice_message_target.show()
            }
        });

        //短信验证码触发
        $Message.on('click', function () {
            message.setOptions({
                captcha_0: $captcha_0.val(),
                captcha_1: $captcha_1.val(),
                phoneNumber: $Message.data('phone')
            });
            message.message_render()
        });

        //语音验证码初始化
        var voice_message = new Message({
            target: $voice_message_target,
            doneCallback: function () {
                $Message.attr('disabled', true)
            },
            timerEndCallback: function () {
                $Message.removeAttr('disabled')
            }
        });

        //语音验证码触发
        $voice_message_target.on('click', '.voice', function (e) {
            voice_message.setOptions({
                phoneNumber: $Message.data('phone')
            });
            voice_message.voice_render();
        });

        //表单验证
        $.validator.addMethod("balance", function (value, element) {
            var balance = $(element).attr('data-balance')
            return (value - balance).toFixed(2) <= 0
        });
        $.validator.addMethod("money", function (value) {
            var re = /^\d+(\.\d{0,2})?$/
            return re.test
            value
        });
        $.validator.addMethod("huge", function (value) {
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
                return $(element).parents('td').children('.form-row-error').html(error)
            },
            submitHandler: function (form) {
                withdraw()
            }
        });

        //提现操作
        var $submit = $('input[type=submit]');
        var withdraw = function () {
            $submit.prop('disabled', true).text('处理中...')
            $.post('/api/withdraw/', {
                card_id: $amount.data('card-id'),
                amount: $amount.val(),
                validate_code: $validate_code.val(),
                trade_pwd: $trade_pwd.val()
            })
                .done(function(result){
                    return tool.modalAlert({
                        title: '温馨提示',
                        msg: result.message
                    });
                })
                .fail(function(xhr){
                    return tool.modalAlert({
                        title: '温馨提示',
                        msg: '系统错误'
                    });
                })
                .always(function(){
                    $submit.prop('disabled', false).text('申请提现');
                })
        }

        //手续费接口
        var checkInput = function (target) {
            var amount = target.val();
            var cardID = target.data('card-id');

            $.post("/api/fee/", {card_id: cardID, amount: amount})
                .done(function (xhr) {
                    var strs;
                    target.parents('td').find('.form-row-error').html('');
                    if (xhr.ret_code > 0) {
                        target.parents('td').find('.form-row-error').html('* ' + xhr.message);
                    } else {
                        if ((xhr.fee === 0) && (xhr.management_fee === 0 || xhr.management_fee === '0')) {
                            strs = '0.00';
                        } else if (xhr.fee !== 0 && (xhr.management_fee === 0 || xhr.management_fee === '0')) {
                            strs = xhr.fee;
                        } else {
                            strs = xhr.fee + '+' + xhr.management_fee;
                        }
                        $('#poundage').html(strs);
                        return $('#actual-amount').text(xhr.actual_amount);
                    }
                });
        };

        //图形验证码
        var refreshCode = function () {
            var url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/anti/captcha/refresh/";
            return $.getJSON(url, {}, function (json) {
                $('input[name="captcha_0"]').val(json.key);
                return $('.captcha-imgs').attr('src', json.image_url);
            });
        };
        //图形验证码首次初始化
        refreshCode();
    });

}).call(this);