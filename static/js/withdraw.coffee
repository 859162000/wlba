require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.placeholder': 'lib/jquery.placeholder'
    'jquery.validate': 'lib/jquery.validate.min'

  shim:
    'jquery.modal': ['jquery']
    'jquery.placeholder': ['jquery']
    'jquery.validate': ['jquery']
)

require ['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder', 'lib/calculator', 'jquery.validate'], ($, modal, backend, placeholder, validate)->

  $.validator.addMethod "balance", (value, element)->
    return backend.checkBalance(value, element)
  $.validator.addMethod "money", (value, element)->
    return backend.checkMoney(value, element) && value < 50000

  $("#withdraw-form").validate
    rules:
      amount:
        required: true
        money: true
        balance: true
      card_id:
        required: true
      validate_code:
        required: true

    messages:
      amount:
        required: '不能为空'
        money: '金额必须在0～50000之间'
        balance: '余额不足'
      card_id:
        required: '请选择银行卡'
      validate_code:
        required: '请输入验证码'

  if $('#id-is-valid').val() == 'False'
    $('#id-validate').modal()

  $("#button-get-validate-code").click (e) ->
    e.preventDefault()

    element = this

    e.preventDefault()
    if $(element).attr 'disabled'
      return;

    phoneNumber = $(element).attr("data-phone")
    $.ajax(
      url: "/api/phone_validation_code/" + phoneNumber + "/"
      type: "POST"
    )

    intervalId
    count = 60

    $(element).attr 'disabled', 'disabled'
    timerFunction = ()->
      if count >= 1
        count--
        $(element).text('重新获取(' + count + ')')
        $(element).addClass('disabled')
      else
        clearInterval(intervalId)
        $(element).text('重新获取')
        $(element).removeAttr 'disabled'
        $(element).removeClass('disabled')

   # Fire now and future
    timerFunction()
    intervalId = setInterval timerFunction, 1000
