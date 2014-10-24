require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->

  Request = new Object()
  Request = backend.getRequest();
  promo_token = Request['promo_token']
  if promo_token
    $("#reg_invitecode").val(promo_token)

  checkMobile = (identifier) ->
    re = undefined
    re = /^1\d{10}$/
    re.test identifier

  $("#button-get-validate-code-modal").click (e) ->
    element = this
    if $(element).hasClass 'disable'
      return
    $(".error-message").text("")
    phoneNumber = $("#reg_identifier").val().trim()
    if checkMobile(phoneNumber)
      $.ajax
          url: "/api/phone_validation_code/register/" + phoneNumber + "/"
          type: "POST"
        .fail (xhr)->
          clearInterval(intervalId)
          $(element).text('重新获取')
          $(element).removeClass 'disable'
          result = JSON.parse xhr.responseText
          $(".error-message").text(result.message)

      intervalId
      count = 60
      $(element).addClass 'disable'

      timerFunction = ()->
        if count >= 1
          count--
          $(element).text('重新获取(' + count + ')')
        else
          clearInterval(intervalId)
          $(element).text('重新获取')
          $(element).removeClass 'disable'
      # Fire now and future
      timerFunction()
      intervalId = setInterval timerFunction, 1000
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
