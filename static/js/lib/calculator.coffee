define ['jquery'], ($)->
  $('input[data-role=earning-calculator]').keyup (e)->
    target = $(e.target)
    rate = target.attr 'data-rate'
    periods = (target.attr 'data-period').split(',')
    amount = target.val()
    unit = (target.attr 'data-unit')
    if unit
      amount = amount * unit
    else
      amount = amount * 10000
    earning_elements = (target.attr 'data-target').split(',')
    for earning_element, i in earning_elements
      period = periods[i]
      $(earning_element).text (rate / 100 * amount / 365 * period).toFixed(1)

  $('input[data-role=fee-calculator]').keyup (e)->
    target = $(e.target)
    rate = target.attr 'data-rate'
    amount = target.val()
    fee_element = target.attr 'data-target-fee'
    actual_element = target.attr 'data-target-actual'
    fee = (rate * amount).toFixed(2)
    actual = (amount - fee).toFixed(2)
    $(fee_element).text fee
    $(actual_element).text actual


