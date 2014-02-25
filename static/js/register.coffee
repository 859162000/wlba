$(document).ready ->
  checkEmail = (identifier) ->
    re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    re.test identifier

  checkMobile = (identifier) ->
    re = /^1\d{10}$/
    re.test identifier

  $('#id_identifier').keyup (e)->
    value = $(this).val()

    isMobile = checkMobile value
    isEmail = checkEmail value

    if isMobile
      $('#validate-code-container').slideDown()
    else
      $('#validate-code-container').hide()

  $('#id_identifier').keyup()

  # Add the validate rule function emailOrPhone
  $.validator.addMethod "emailOrPhone", (value, element)->
    return checkEmail(value) or checkMobile(value)

  $('#register-form').validate {
    rules:
      identifier:
        required: true
        emailOrPhone: true
      password:
        required: true
        minlength: 6
      'validation_code':
        required: true
        depends: (e)->
          checkMobile($('#id_identifier').val())

    messages:
      identifier:
        required: '不能为空'
        depends: '请输入邮箱或者手机号'
      password:
        required: '不能为空'
        minlength: $.format("密码需要最少{0}位")
      'validation_code':
        required: '不能为空'
  }

  $('#button-get-validate-code').click (e)->
    element = this

    e.preventDefault()
    alert('send ajax to server to send ajax')

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
