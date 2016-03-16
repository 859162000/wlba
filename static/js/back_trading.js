// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.validate': 'lib/jquery.validate.min',
      'jquery.modal': 'lib/jquery.modal.min',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.validate': ['jquery'],
      'jquery.modal': ['jquery'],
      "tools": ['jquery.modal']
    }
  });

  require(['jquery', 'jquery.validate', 'lib/backend', 'tools'], function($, validate, backend, tool) {
    $('#passwordChangeButton').click(function(e) {
      var params;
      e.preventDefault();
      if ($('#passwordChangeForm').valid()) {
          params = {
            old_trade_pwd: $('#old_trade_pwd').val(),
            new_trade_pwd: $('#new_trade_pwd').val(),
            action_type: 2,
            requirement_check: 0
          };
          return backend.changeTradingPwd(params).done(function(data) {
            $('#passwordChangeForm').find('input').val('');
            if (data.ret_code === 0) {
              return tool.modalAlert({
                btnText: "确认",
                title: '温馨提示',
                msg: '交易密码修改成功',
                callback_ok: function() {
                  return window.location.href = '/accounts/setting/';
                }
              });
            } else {
              return tool.modalAlert({
                btnText: "确认",
                title: '温馨提示',
                msg: '交易密码修改失败,请重试',
                callback_ok: function() {
                  return $.modal.close();
                }
              });
            }
          });
      }
    });
    $('#passwordChangeForm').validate({
      rules: {
        'old_trade_pwd': {
          required: true
        },
        'new_trade_pwd': {
          required: true,
          minlength: 6
        },
        'new_trade_pwd2': {
          required: true,
          equalTo: "#new_trade_pwd"
        }
      },
      messages: {
        'old_trade_pwd': {
          required: '不能为空'
        },
        'new_trade_pwd': {
          required: '不能为空',
          minlength: $.format("密码需要最少{0}位")
        },
        'new_trade_pwd2': {
          required: '不能为空',
          equalTo: '两次密码输入不一致'
        }
      }
    });

  });

}).call(this);

//# sourceMappingURL=account_setting.js.map