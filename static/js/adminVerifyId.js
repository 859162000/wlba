// Generated by CoffeeScript 1.9.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'jquery.validate': 'lib/jquery.validate.min',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.validate': ['jquery']
    }
  });

  require(['jquery', 'lib/modal', 'lib/backend', 'jquery.validate', 'tools'], function($, modal, backend, validate, tool) {
    $.validator.addMethod("emailOrPhone", function(value, element) {
      return backend.checkEmail(value) || backend.checkMobile(value);
    });
    $.validator.addMethod('idNumber', function(value, element) {
      var reg;
      reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
      return reg.test(value);
    }, '请输入有效身份证');
    return $('#validate_id_form').validate({
      rules: {
        phone: {
          required: true,
          emailOrPhone: true
        },
        name: {
          required: true
        },
        id_number: {
          required: true,
          idNumber: true
        }
      },
      messages: {
        phone: {
          required: '手机号不能为空',
          emailOrPhone: '请正确的手机号'
        },
        name: {
          required: '请输入姓名'
        },
        id_number: {
          required: '请输入身份证',
          idNumber: '请输入有效身份证'
        }
      },
      errorPlacement: function(error, element) {
        return error.appendTo($(element).closest('.form-row').find('.form-row-error'));
      },
      submitHandler: function(form) {
        var id_number, name, phone;
        phone = $('#id_phone').val();
        name = $('#id_name').val();
        id_number = $('#id_id_number').val();
        if ($("#validate_id_button").hasClass("disabled")) {
          return;
        }
        $("#validate_id_button").addClass('disabled');
        return $.ajax({
          url: '/api/admin_id_validate/',
          data: {
            phone: phone,
            name: name,
            id_number: id_number
          },
          type: 'post'
        }).done(function() {
          return tool.modalAlert({
            title: '温馨提示',
            msg: '实名认证成功',
            callback_ok: function() {
              return location.reload();
            }
          });
        }).fail(function(xhr) {
          var result;
          $(this).removeClass('disabled');
          result = JSON.parse(xhr.responseText);
          if (result.error_number === 8) {
            tool.modalAlert({
              title: '温馨提示',
              msg: '验证失败，请拨打客服电话进行人工验证。4008-588-066'
            });
            return;
          }
          return tool.modalAlert({
            title: '温馨提示',
            msg: result.message
          });
        });
      }
    });
  });

}).call(this);

//# sourceMappingURL=adminVerifyId.js.map
