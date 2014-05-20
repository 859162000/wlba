define ['jquery'], ($)->
  $('input[data-role=earning-calculator]').keyup (e)->
    target = $(e.target)
    rate = target.attr 'data-rate'
    periods = (target.attr 'data-period').split(',')
    amount = target.val()
    earning_elements = (target.attr 'data-target').split(',')
    for earning_element, i in earning_elements
      period = periods[i]
      $(earning_element).text (rate / 100 * amount * 10000 / 365 * period).toFixed(1)

    console.log 'rate: ' + rate + ' amount:' + amount


