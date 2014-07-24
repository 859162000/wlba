require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'

require ['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown'], ($, _, backend, calculator, countdown)->
  $('#purchase-form .submit-button').click (e)->
    e.preventDefault()

    if !confirm('您的投资金额为:' + $('input[name=amount]').val())
      return

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
      message = result.message
      error_message = ''
      if $.type(message) == 'object'
        error_message = _.chain(message).pairs().map((e)->e[1]).flatten().value()
      else
        error_message = message

      alert error_message
      location.reload()
