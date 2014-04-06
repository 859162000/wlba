define ['jquery'], ($)->
  $('input[data-role=earning-calculator]').keyup (e)->
    target = $(e.target)
    rate = target.attr 'data-rate'
    period = target.attr 'data-period'
    amount = target.val()
    earning_element = $(target.attr 'data-target')

    console.log 'rate: ' + rate + ' amount:' + amount
    earning_element.text (rate / 100 * amount * 10000 / 365 * period).toFixed(1)
