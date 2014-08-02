require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    tools: 'lib/modal.tools'

require ['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown', 'tools'], ($, _, backend, calculator, countdown, tool)->

  handler = () ->
      product = $('input[name=product]').val()
      amount = $('input[name=amount]').val()
      captcha_0 = $('input[name=captcha_0]').val()
      captcha_1 = $('input[name=captcha_1]').val()

      backend.purchaseP2P {
        product: product
        amount: amount
        captcha_0: captcha_0
        captcha_1: captcha_1
      }
      .done (data)->
        alert '份额认购成功'
        location.reload()
      .fail (xhr)->
        result = JSON.parse xhr.responseText
        if result.error_number == 1
          $('.login-modal').trigger('click')
          return
        else if result.error_number == 2
          $('#id-validate').modal()
          return

        message = result.message
        error_message = ''
        if $.type(message) == 'object'
          error_message = _.chain(message).pairs().map((e)->e[1]).flatten().value()
        else
          error_message = message

        #alert error_message
        tool.modalAlert({title: '温馨提示', msg: error_message})

  $('#purchase-form .submit-button').click (e)->
    e.preventDefault()

    tip = '您的投资金额为:' + $('input[name=amount]').val() + '元'
    tool.modalConfirm({title: '温馨提示', msg: tip, callback_ok: handler})
