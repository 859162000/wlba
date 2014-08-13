require.config
  paths:
    jquery: 'lib/jquery.min'
    tools: 'lib/modal.tools'

require ['jquery', 'tools'], ($, tool)->
  $('#setPasswordButton').click (e)->
    e.preventDefault()
    password1 = $('#new_password1').val()
    password2 = $('#new_password2').val()
    if password1.length < 6 || password1.length > 20
      tool.modalAlert({title: '温馨提示', msg: '密码长度为6-20位'})
      return
    if password1 != password2
      tool.modalAlert({title: '温馨提示', msg: '两次密码输入不一致'})
      return
    else
      $.post '/accounts/password/reset/set_password/', { password1: password1 ,password2: password2}
      .done ->
        location.href = '/accounts/password/reset/done/'
      .fail ->
        tool.modalAlert({title: '温馨提示', msg: '更改密码失败 请重试'})
