require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.validate': 'lib/jquery.validate.min'
    'jquery.modal': 'lib/jquery.modal.min'
    tools: 'lib/modal.tools'

  shim:
    'jquery.validate': ['jquery']
    'jquery.modal' : ['jquery']
    "tools": ['jquery.modal']

require ['jquery', 'jquery.validate', 'lib/backend', 'tools'], ($, validate, backend, tool)->
  $('#passwordChangeButton').click (e)->
    e.preventDefault()

    if $('#passwordChangeForm').valid()
      params =
        old_password: $('#old-password').val()
        new_password1: $('#new-password1').val()
        new_password2: $('#new-password2').val()
      backend.changePassword params
      .done ->
        $('#passwordChangeForm').find('input').val('')
        tool.modalAlert({btnText:"确认", title: '温馨提示', msg: '密码修改成功，请重新登录', callback_ok: ()->
          window.location.href = '/accounts/logout/?next=/accounts/login/'
        })
      .fail ->
        console.log 'Failed to update password, do it again'
        tool.modalAlert({btnText:"确认", title: '温馨提示', msg: '密码修改失败 请重试'})

  $('#passwordChangeForm').validate
    rules:
      'old-password':
        required: true
      'new-password1':
        required: true
        minlength: 6
      'new-password2':
        required: true
        equalTo: "#new-password1"

    messages:
      'old-password':
        required: '不能为空'
      'new-password1':
        required: '不能为空'
        minlength: $.format("密码需要最少{0}位")
      'new-password2':
        required: '不能为空'
        equalTo: '两次密码输入不一致'

  ###判断是否设置了交易密码###
  $.ajax
    url: "/api/profile/"
    type: "GET"
    data: {
    }
  .success (date) ->
    if date.trade_pwd_is_set
      $('.old').show()
    else
      $('.new').show()
  $.ajax
      url: "/api/pay/the_one_card/"
      type: "GET"
      data: {}
    .fail ()->
      $('#bankIsNoBind').val('false')
    .done (xhr) ->
      $('#bankIsNoBind').val('true')

  ###找回交易密码###
  $('#getBackTradingPwd').click ->
    if $('#bankIsNoBind').val() == 'false'
      $('#goBindingBackWin').modal();
    else
      window.location.href = '/accounts/trading/back/'
  $('#temporaryNot').click ->
    $.modal.close()


