// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.validate': 'lib/jquery.validate.min',
      'jquery.placeholder': 'lib/jquery.placeholder'
    },
    shim: {
      'jquery.validate': ['jquery'],
      'jquery.placehoder': ['jquery']
    }
  });

  require(['jquery', 'jquery.validate', 'lib/backend', 'jquery.placeholder'], function($, validate, backend, placeholder) {
    $('input, textarea').placeholder();
    $.validator.addMethod("emailOrPhone", function(value, element) {
      return backend.checkEmail(value) || backend.checkMobile(value);
    });
    return $('#login-form').validate({
      rules: {
        identifier: {
          required: true,
          emailOrPhone: true
        },
        password: {
          required: true,
          minlength: 6
        }
      },
      messages: {
        identifier: {
          required: '不能为空',
          emailOrPhone: '请输入邮箱或者手机号'
        },
        password: {
          required: '不能为空',
          minlength: $.format("密码需要最少{0}位")
        }
      }
    });
  });

}).call(this);

//# sourceMappingURL=login.map
