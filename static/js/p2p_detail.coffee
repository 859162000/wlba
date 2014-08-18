require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    tools: 'lib/modal.tools'
    "jquery.validate": 'lib/jquery.validate.min'

  shims:
    "jquery.validate": ['jquery']

require ['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown', 'tools'], ($, _, backend, calculator, countdown, tool)->

  $.validator.addMethod 'dividableBy100', (value, element)->
    return value % 100 == 0
  , '请输入100的整数倍'

  $.validator.addMethod 'positiveNumber', (value, element)->
    return Number(value) > 0
  , '请输入有效金额'

  $('#purchase-form').validate
    rules:
      amount:
        required: true
        number: true
        positiveNumber: true
        dividableBy100: true

    messages:
      amount:
        required: '请输入投资金额'
        number: '请输入有效金额'

    errorPlacement: (error, element) ->
      error.appendTo $(element).closest('.form-row').find('.form-row-error')

    submitHandler: (form)->
      tip = '您的投资金额为:' + $('input[name=amount]').val() + '元'
      tool.modalConfirm({title: '温馨提示', msg: tip, callback_ok: ()->
        product = $('input[name=product]').val()
        amount = $('input[name=amount]').val()
        validate_code = $('input[name=validate_code]').val()

        backend.purchaseP2P {
          product: product
          amount: amount
          validate_code: validate_code
        }
        .done (data)->
          tool.modalAlert({title: '温馨提示', msg: '份额认购成功', callback_ok: ()->
              location.reload()
          })

        .fail (xhr)->
          result = JSON.parse xhr.responseText
          if result.error_number == 1
            $('.login-modal').trigger('click')
            return
          else if result.error_number == 2
            $('#id-validate').modal()
            return
          else if result.error_number == 4 && result.message == "余额不足"
            tool.modalAlert({btnText:"去充值", title: '温馨提示', msg: result.message, callback_ok: ()->
              window.location.href = '/pay/banks/'
            })
            return

          message = result.message
          error_message = ''
          if $.type(message) == 'object'
            error_message = _.chain(message).pairs().map((e)->e[1]).flatten().value()
          else
            error_message = message

          tool.modalAlert({title: '温馨提示', msg: error_message})
      })

  $("#get-validate-code-buy").click () ->
    element = this
    if $(element).hasClass 'disabled'
      return

    phoneNumber = $(element).attr("data-phone")
    if !phoneNumber
      return
    $.ajax(
      url: "/api/phone_validation_code/" + phoneNumber + "/"
      type: "POST"
    )

    intervalId
    count = 60

    timerFunction = ()->
      if count >= 1
        count--
        $(element).text('重新获取(' + count + ')')
        if !$(element).hasClass('disabled')
          $(element).addClass('disabled')
      else
        clearInterval(intervalId)
        $(element).text('重新获取')
        $(element).removeClass('disabled')

   # Fire now and future
    timerFunction()
    intervalId = setInterval timerFunction, 1000

  $('#purchase-form .submit-button').click (e)->
    e.preventDefault()
    $('#purchase-form').submit()



