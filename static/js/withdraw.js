// Generated by CoffeeScript 1.7.1
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
    $('input, textarea').placeholder();
    $('#add-card-button').click(function(e) {
      e.preventDefault();
      return $(this).modal();
    });
    $('#add-card').click(function(e) {
      var bank_id, card_no, is_default;
      e.preventDefault();
      card_no = $('#card-no').val();
      if (!backend.checkCardNo(card_no)) {
        alert('请输入有效的银行卡号');
        return;
      }
      bank_id = $('#bank-select').val();
      if (!bank_id) {
        alert('请选择银行');
        return;
      }
      is_default = $('#default-checkbox').prop('checked');
      return $.ajax({
        url: '/api/card/',
        data: {
          no: card_no,
          bank: bank_id,
          is_default: is_default
        },
        type: 'post'
      }).done(function() {
        return location.reload();
      }).fail(function() {
        return alert('添加银行卡失败');
      });
    });
    $.validator.addMethod("balance", function(value, element) {
      return backend.checkBalance(value, element);
    });
    $.validator.addMethod("money", function(value, element) {
      return backend.checkMoney(value, element);
    });
    return $("#withdraw-form").validate({
      rules: {
        amount: {
          required: true,
          money: true,
          balance: true
        },
        card_id: {
          required: true
        }
      },
      messages: {
        amount: {
          required: '不能为空',
          money: '金额必须为正的两位小数',
          balance: '余额不足'
        },
        card_id: {
          required: '请选择银行卡'
        }
      }
    });
  });

}).call(this);

//# sourceMappingURL=withdraw.map
