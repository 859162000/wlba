(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'jquery.placeholder': 'lib/jquery.placeholder',
      'jquery.validate': 'lib/jquery.validate.min'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.placeholder': ['jquery'],
      'jquery.validate': ['jquery']
    }
  });
  require(['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder', 'lib/calculator', 'jquery.validate'], function($, modal, backend, placeholder, validate) {
    $.validator.addMethod("balance", function(value, element) {
      return backend.checkBalance(value, element);
    });
    $.validator.addMethod("money", function(value, element) {
      return backend.checkMoney(value, element);
    });
    $.validator.addMethod("huge", function(value, element) {
      return value <= 50000;
    });
    $.validator.addMethod("small", function(value, element) {
      var balance;
      balance = $(element).attr('data-balance');
      if (value <= 0) {
        return false;
      }
      if (balance - value === 0) {
        return true;
      } else if (value >= 50) {
        return true;
      }
      return false;
    });
    $("#withdraw-form").validate({
      rules: {
        amount: {
          required: true,
          money: true,
          balance: true,
          huge: true,
          small: true
        },
        card_id: {
          required: true
        },
        validate_code: {
          required: true
        }
      },
      messages: {
        amount: {
          required: '不能为空',
          money: '请输入正确的金额格式',
          balance: '余额不足',
          huge: '提现金额不能超过50000',
          small: '最低提现金额 50 元起。如果余额低于 50 元，请一次性取完。'
        },
        card_id: {
          required: '请选择银行卡'
        },
        validate_code: {
          required: '请输入验证码'
        }
      }
    });
    if ($('#id-is-valid').val() === 'False') {
      $('#id-validate').modal();
    }
    return $("#button-get-validate-code").click(function(e) {
      var count, element, intervalId, phoneNumber, timerFunction;
      e.preventDefault();
      element = this;
      e.preventDefault();
      if ($(element).attr('disabled')) {
        return;
      }
      phoneNumber = $(element).attr("data-phone");
      $.ajax({
        url: "/api/phone_validation_code/" + phoneNumber + "/",
        type: "POST"
      });
      intervalId;
      count = 60;
      $(element).attr('disabled', 'disabled');
      timerFunction = function() {
        if (count >= 1) {
          count--;
          $(element).text('重新获取(' + count + ')');
          return $(element).addClass('disabled');
        } else {
          clearInterval(intervalId);
          $(element).text('重新获取');
          $(element).removeAttr('disabled');
          return $(element).removeClass('disabled');
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    });
  });
}).call(this);
