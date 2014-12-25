require.config
  paths:
    jquery: 'lib/jquery.min'
    jquerymobile: 'lib/jquery.mobile.custom.min'

require ['jquery', 'lib/backend', 'jquerymobile'], ($, backend, mobile)->
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
      $('#sendValidateCodeButton').prop('disabled', false)

    _countDown()


  Request = new Object()
  Request = backend.getRequest();
  req_identifier = Request['identifier']
  if req_identifier
    $(".re_identifier").text(req_identifier)
    $("#reg_identifier").val(reg_identifier)

  checkMobile = (identifier) ->
    re = undefined
    re = /^1\d{10}$/
    re.test identifier

  $("#button-get-validate-code-modal").click (e) ->
    element = this
    if $(element).hasClass 'disable'
      return
    $(".error-message").text("")
    identifier = $("#reg_identifier").val().trim()
    if !identifier
      $(".error-message").text("请输入手机号")
    if checkMobile(identifier)
      if identifier == $("#hidden_identifier").val()
        $(".error-message").text("自己不能邀请自己")
      else
        backend.userExists identifier
        .done ->
          $(".popup-message").text("您输入的手机号已注册过网利宝！")
          $("#popupDialog").popup('open')
          $("#popupDialog").on "popupafterclose", ()->
            window.location.href = "#stepDownloadOld"
            return true
        .fail ->
          $(".popup-message").text("验证码已发送至您手机，请注意查收。")
          $("#popupDialog").popup('open')
          $("#popupDialog").on "popupafterclose", ()->
            $(".re_identifier").text(identifier)
            $("#reg_identifier").val(identifier)
            window.location.href = "?identifier=" + identifier + "#stepRegister"
            _countDown()
            return true
    else
      $(".error-message").text("手机号输入错误")

  $("#register_submit").click (e)->
    element = this;
    if $(element).hasClass("disable")
      return
    $(".error-message").text("")
    identifier = $("#reg_identifier").val().trim()
    if !checkMobile(identifier)
      $(".error-message").text("手机号输入错误")
      return

    validate_code = $("#id_validate_code").val().trim()
    if validate_code.length != 6
      $(".error-message").text("请输入6位验证码")
      return

    invite_code = $("#reg_invitecode").val().trim()
    if invite_code.length > 0 && invite_code.length != 6
      $(".error-message").text("请输入6位邀请码")
      return
    $(element).addClass 'disable'
    backend.registerWap {
          identifier: identifier
          validate_code: validate_code
          invite_code: invite_code
        }
    .done (data)->
      if data.ret_code > 0
        $(element).removeClass 'disable'
        $(".error-message").text(data.message)
      else
        window.location.href = '/'
    .fail ()->
      $(".error-message").text("注册失败")
