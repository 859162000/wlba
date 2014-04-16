require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.validate': 'lib/jquery.validate.min'

  shim:
    'jquery.validate': ['jquery']

require ['jquery', 'jquery.validate', 'lib/backend'], ($, validate, backend)->
  checkEmail = (identifier) ->
    re = undefined
    re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    re.test identifier

  checkMobile = (identifier) ->
    re = undefined
    re = /^1\d{10}$/
    re.test identifier

  $("#id_identifier").keyup (e) ->
    isEmail = undefined
    isMobile = undefined
    value = undefined
    value = $(this).val()
    isMobile = checkMobile(value)
    isEmail = checkEmail(value)
    if isMobile
      $("#id_type").val "phone"
      $("#validate-code-container").show()
    else if isEmail
      $("#id_type").val "email"
      $("#validate-code-container").hide()
    else
      $("#id_type").val "email"
      $("#validate-code-container").hide()

  $("#id_identifier").keyup()
  $("#button-get-validate-code").click (e) ->
    e.preventDefault()

    element = this

    e.preventDefault()

    phoneNumber = $("#id_identifier").val().trim()
    if checkMobile(phoneNumber)
      if console?
        console.log "Phone number checked, now send the valdiation code"

      $.ajax(
        url: "/api/phone_validation_code/register/" + phoneNumber + "/"
        type: "POST"
      )

      intervalId
      count = 60

      $(element).attr 'disabled', 'disabled'
      timerFunction = ()->
        if count >= 1
          count--
          $(element).text('重新获取(' + count + ')')
        else
          clearInterval(intervalId)
          $(element).text('重新获取')
          $(element).removeAttr 'disabled'

      # Fire now and future
      timerFunction()
      intervalId = setInterval timerFunction, 1000

  # Add the validate rule function emailOrPhone
  $.validator.addMethod "emailOrPhone", (value, element)->
    return checkEmail(value) or checkMobile(value)

  $('#register-form').validate
    rules:
      identifier:
        required: true
        emailOrPhone: true
      password:
        required: true
        minlength: 6
      password2:
        equalTo: "#id_password"
      'validation_code':
        required: true
        depends: (e)->
          checkMobile($('#id_identifier').val())

    messages:
      identifier:
        required: '不能为空'
        emailOrPhone: '请输入邮箱或者手机号'
      password:
        required: '不能为空'
        minlength: $.format("密码需要最少{0}位")
      'validation_code':
        required: '不能为空'
      password2:
        equalTo: '密码不一致'
