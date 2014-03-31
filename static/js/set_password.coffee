require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery'], ($)->
  $('#setPasswordButton').click (e)->
    password1 = $('input[name="password1"').val()
    password2 = $('input[name="password2"').val()

    if password1 != password2
      console.log 'Password not match'
    else
      $.post '/accounts/password_reset_password', {
        password1: password1
        password2: password2
      }
      .done ->
        window.location = 'http://www.baidu.com'
      .fail ->
        # TODO notify people when failed
        console.log '更改密码失败 请重试'
