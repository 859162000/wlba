require.config
  paths:
    jquery: 'lib/jquery.min'
    tools: 'lib/modal.tools'

require ['jquery', 'lib/backend', 'tools'], ($, backend, tool)->
  _countDown = ()->
    element = $('#sendValidateCodeButton')
    count = 60
    $(element).prop 'disabled', true

    timerFunction = ()->
      if count >= 1
        count--
        $(element).html('已经发送(' + count + ')')
        $(element).addClass("disabled")
      else
        clearInterval(intervalId)
        $(element).html('重新获取')
        $(element).prop 'disabled', false
        $(element).removeClass("disabled")

    # Fire now and future
    timerFunction()
    intervalId = setInterval timerFunction, 1000

  $('#sendValidateCodeButton').click (event)->
    target = $(event.target).attr('data-url')
    $.post target
    .done ->
      $('#nextStep').prop('disabled', false)

    _countDown()


  $('#nextStep').click (e)->
    # Check the validate code first
    target = $(e.target).attr('data-url')
    validate_code = $('input[name="validate_code"]').val()

    if validate_code == ''
      tool.modalAlert({title: '温馨提示', msg: '验证码不能为空'})
      return

    $.post target, {
        "validate_code": validate_code
      }
      .done ->
        # If succeeded, then go to password setting page
        window.location = '/accounts/password/reset/set_password/'
      .fail ->
        tool.modalAlert({title: '温馨提示', msg: '验证失败!'})

  $('#validate_form').on 'submit', (e) ->
    e.preventDefault()
    $('#nextStep').click()
  _countDown()

