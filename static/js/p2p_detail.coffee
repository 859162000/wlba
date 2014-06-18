require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  $('#purchase-form .submit-button').click (e)->
    e.preventDefault()
    console.log 'clicked'

    product = $('input[name=product]').val()
    amount = $('input[name=amount]').val()
    captcha_0 = $('input[name=captcha_0').val()
    captcha_1 = $('input[name=captcha_1]').val()

    backend.purchaseP2P {
      product: product
      amount: amount
      captcha_0: captcha_0
      captcha_1: captcha_1
    }
    .done (data)->
      location.reload()
    .fail (xhr)->
      console.log "failed"
