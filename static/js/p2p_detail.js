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
    $.validator.addMethod('positiveNumber', function(value, element) {
      return Number(value) > 0;
    }, '请输入有效金额');
    $('#purchase-form').validate({
      rules: {
        amount: {
          required: true,
          number: true,
          positiveNumber: true,
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
        return error.appendTo($(element).closest('.form-row__middle').find('.form-row-error'));
      },
      submitHandler: function(form) {
        var tip;
        tip = '您的投资金额为:' + $('input[name=amount]').val() + '元';
        return tool.modalConfirm({
          title: '温馨提示',
          msg: tip,
          callback_ok: function() {
            var amount, product, validate_code;
            product = $('input[name=product]').val();
            amount = $('input[name=amount]').val();
            validate_code = $('input[name=validate_code]').val();
            return backend.purchaseP2P({
              product: product,
              amount: amount,
              validate_code: validate_code
            }.done(function(data) {
              return tool.modalAlert({
                title: '温馨提示',
                msg: '份额认购成功',
                callback_ok: function() {
                  return location.reload();
                }
              });
            })).fail(function(xhr) {
              var error_message, message, result;
              result = JSON.parse(xhr.responseText);
              if (result.error_number === 1) {
                $('.login-modal').trigger('click');
                return;
              } else if (result.error_number === 2) {
                $('#id-validate').modal();
                return;
              } else if (result.error_number === 4 && result.message === "余额不足") {
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
    $("#get-validate-code-buy").click(function() {
      var count, element, intervalId, phoneNumber, timerFunction;
      element = this;
      if ($(element).hasClass('disabled')) {
        return;
      }
      phoneNumber = $(element).attr("data-phone");
      if (!phoneNumber) {
        return;
      }
      $.ajax({
        url: "/api/phone_validation_code/" + phoneNumber + "/",
        type: "POST"
      });
      intervalId;
      count = 60;
      timerFunction = function() {
        if (count >= 1) {
          count--;
          $(element).text('重新获取(' + count + ')');
          if (!$(element).hasClass('disabled')) {
            return $(element).addClass('disabled');
          }
        } else {
          clearInterval(intervalId);
          $(element).text('重新获取');
          return $(element).removeClass('disabled');
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    });
    return $('#purchase-form .submit-button').click(function(e) {
      e.preventDefault();
      return $('#purchase-form').submit();
    });
  });
}).call(this);
