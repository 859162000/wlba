require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->


  checkMobile = (identifier) ->
    re = undefined
    re = /^1\d{10}$/
    re.test identifier

  $("#button-get-validate-code-modal").click (e) ->
    element = this
    if $(element).hasClass 'disable'
      return
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
    if $(this).hasClass("disable")
      return
    $(this).addClass 'disable'
    identifier = $("#reg_identifier").val().trim()
    validate_code = $("#id_validate_code").val().trim()
    invite_code = $("#reg_invitecode").val().trim()
    backend.registerWap {
          identifier: identifier
          validate_code: validate_code
          invite_code: invite_code
        }
    .done (data)->
      window.location.href = 'www.wanglibao.com'
    .fail ()->
      $(".error-message").text("手机号输入错误")
