require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  _countDown = ()->
    element = $('#sendValidateCodeButton')

    intervalId
    count = 60
    $(element).addClass 'disabled'
    $(element).prop 'disabled', true

    timerFunction = ()->
      if count >= 1
        count--
        $(element).text('已经发送(' + count + ')')
      else
        clearInterval(intervalId)
        $(element).text('重新获取')
        $(element).prop 'disabled', false
        $(element).removeClass 'disabled'

    timerFunction()
    intervalId = setInterval timerFunction, 1000

  _countDown()

  $('#sendValidateCodeButton').click (event)->
    element = this
    if $(element).hasClass 'disabled'
      return
    target = $(event.target).attr('data-url')
    $.post target
    .done ->
      $('#sendValidateCodeButton').addClass 'disabled'

    _countDown()

  $("#register_submit").click (e)->
    element = this;
    if $(element).hasClass "disabled"
      return
    $(".error-message").text("")
    identifier = $("#reg_identifier").val().trim()
    reg_password = $("#reg_password").val().trim()
    validate_code = $("#reg_validate_code").val().trim()
    invite_code = $("#reg_invitecode").val().trim()

    if validate_code.length != 6
      $(".error-message").text("请输入6位验证码")
      return
    if !reg_password && reg_password.length < 6
      $(".error-message").text("请输入密码")
      return

    $(element).addClass 'disabled'
    $(element).prop 'disabled', true
    ajax_url = $("#register-form").attr('action')
    console.log ajax_url
    backend.registerShare {
        identifier: identifier
        password: reg_password
        validate_code: validate_code
        invite_code: invite_code
      }
    .done (data,textStatus) ->
      if data.ret_code > 0
        $(element).removeClass 'disabled'
        $(element).prop 'disabled', false
        $(".error-message").text(data.message)
      else
        window.location.href = "/activity/wap/share?phone=" + identifier + "&reg=y"
    .fail (xhr)->
      alert("注册失败。\n您可以去网利宝网站（www.wanglibao.com）试试。")
      window.location.href = "/"

