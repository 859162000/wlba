require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.validate': 'lib/jquery.validate.min'
    'jquery.placeholder': 'lib/jquery.placeholder'

  shim:
    'jquery.validate': ['jquery']
    'jquery.placehoder': ['jquery']

require ['jquery', 'jquery.validate', 'lib/backend', 'jquery.placeholder'], ($, validate, backend, placeholder)->

  $('input, textarea').placeholder()

# Add the validate rule function emailOrPhone
  $.validator.addMethod "emailOrPhone", (value, element)->
    return backend.checkEmail(value) or backend.checkMobile(value)

  $('#login-form').validate
    rules:
      identifier:
        required: true
        emailOrPhone: true
      password:
        required: true
        minlength: 6

    messages:
      identifier:
        required: '不能为空'
        emailOrPhone: '请输入邮箱或者手机号'
      password:
        required: '不能为空'
        minlength: $.format("密码需要最少{0}位")

