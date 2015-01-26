require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->

  getCookie = (name) ->
    cookieValue = null
    if document.cookie and document.cookie isnt ""
      cookies = document.cookie.split(";")
      i = 0
      while i < cookies.length
        cookie = $.trim(cookies[i])

        # Does this cookie string begin with the name we want?
        if cookie.substring(0, name.length + 1) is (name + "=")
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        i++
    cookieValue

  csrfSafeMethod = (method) ->
    # these HTTP methods do not require CSRF protection
    /^(GET|HEAD|OPTIONS|TRACE)$/.test method

  sameOrigin = (url) ->
    # test that a given url is a same-origin URL
    # url could be relative or scheme relative or absolute
    host = document.location.host # host + port
    protocol = document.location.protocol
    sr_origin = "//" + host
    origin = protocol + sr_origin

    # Allow absolute or scheme relative URLs to same origin

    # or any other URL that isn't scheme relative or absolute i.e relative.
    (url is origin or url.slice(0, origin.length + 1) is origin + "/") or (url is sr_origin or url.slice(0, sr_origin.length + 1) is sr_origin + "/") or not (/^(\/\/|http:|https:).*/.test(url))


  $.ajaxSetup beforeSend: (xhr, settings) ->
    if not csrfSafeMethod(settings.type) and sameOrigin(settings.url)

    # Send the token to same-origin, relative URLs only.
    # Send the token only if the method warrants CSRF protection
    # Using the CSRFToken value acquired earlier
      xhr.setRequestHeader "X-CSRFToken", getCookie("csrftoken")
    return

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
    if $(element).hasClass 'disabled'
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
          $(element).removeClass 'disabled'
          result = JSON.parse xhr.responseText
          $(".error-message").text(result.message)

      intervalId
      count = 60
      $(element).addClass 'disabled'
      $(element).attr 'disabled', 'disabled'

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
