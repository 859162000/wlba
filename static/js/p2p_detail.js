// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      tools: 'lib/modal.tools',
      "jquery.validate": 'lib/jquery.validate.min'
    },
    shims: {
      "jquery.validate": ['jquery']
    }
  });

  require(['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown', 'tools'], function($, _, backend, calculator, countdown, tool) {
    $.validator.addMethod('dividableBy100', function(value, element) {
      return value % 100 === 0;
    }, '请输入100的整数倍');
    $('#purchase-form').validate({
      rules: {
        amount: {
          required: true,
          number: true,
          dividableBy100: true
        }
      },
      messages: {
        amount: {
          required: '请输入投资金额',
          number: '请输入有效金额'
        }
      },
      errorPlacement: function(error, element) {
        return error.appendTo($(element).closest('.form-row').find('.form-row-error'));
      },
      submitHandler: function(form) {
        var tip;
        tip = '您的投资金额为:' + $('input[name=amount]').val() + '元';
        return tool.modalConfirm({
          title: '温馨提示',
          msg: tip,
          callback_ok: function() {
            var amount, captcha_0, captcha_1, product;
            product = $('input[name=product]').val();
            amount = $('input[name=amount]').val();
            captcha_0 = $('input[name=captcha_0]').val();
            captcha_1 = $('input[name=captcha_1]').val();
            return backend.purchaseP2P({
              product: product,
              amount: amount,
              captcha_0: captcha_0,
              captcha_1: captcha_1
            }).done(function(data) {
              alert('份额认购成功');
              return location.reload();
            }).fail(function(xhr) {
              var error_message, message, result;
              result = JSON.parse(xhr.responseText);
              if (result.error_number === 1) {
                $('.login-modal').trigger('click');
                return;
              } else if (result.error_number === 2) {
                $('#id-validate').modal();
                return;
              } else if (result.error_number === 4 && result.message === "余额不足") {
                console.log("dfsd");
                tool.modalAlert({
                  btnText: "去充值",
                  title: '温馨提示',
                  msg: result.message,
                  callback_ok: function() {
                    return window.location.href = '/pay/banks/';
                  }
                });
                return;
              }
              message = result.message;
              error_message = '';
              if ($.type(message) === 'object') {
                error_message = _.chain(message).pairs().map(function(e) {
                  return e[1];
                }).flatten().value();
              } else {
                error_message = message;
              }
              return tool.modalAlert({
                title: '温馨提示',
                msg: error_message
              });
            });
          }
        });
      }
    });
    return $('#purchase-form .submit-button').click(function(e) {
      e.preventDefault();
      return $('#purchase-form').submit();
    });
  });

}).call(this);

//# sourceMappingURL=p2p_detail.map
