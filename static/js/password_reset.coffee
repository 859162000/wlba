require.config
  paths:
    jquery: 'lib/jquery.min'
    tools: 'lib/modal.tools'

require ['jquery', 'lib/backend', 'tools'], ($, backend, tool)->
  submit_form = ()->
    identifier = $('input[name="identifier"]').val()
    if !identifier
      tool.modalAlert({title: '温馨提示', msg: '请输入手机号'})
      return
    backend.userExists identifier
    .done ->
      $('form#identifier').submit()
      return true
    .fail ->
      tool.modalAlert({title: '温馨提示', msg: '该用户不存在'})

  $('#submitButton').click (e)->
    e.preventDefault()
    submit_form()

  $('input').keyup (e)->
    if e.keyCode == 13
      e.preventDefault()
      submit_form()

