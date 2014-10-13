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
      earning = (rate / 100 * amount / 365 * period).toFixed(1)
      if earning and $.isNumeric(earning)
        $(earning_element).text earning
      else
        $(earning_element).text "0.0"


  $('input[data-role=fee-calculator]').keyup (e)->
    target = $(e.target)
    rate = target.attr 'data-rate'
    amount = target.val()
    fee_element = target.attr 'data-target-fee'
    actual_element = target.attr 'data-target-actual'
    fee = (rate * amount).toFixed(2)
    actual = (amount - fee).toFixed(2)
    if fee and $.isNumeric(fee)
      $(fee_element).text fee
    else
      $(fee_element).text "0.00"

    if actual and $.isNumeric(actual)
      $(actual_element).text actual
    else
      $(actual_element).text "0.00"



  $('input[data-role=fee-calculator]').keyup()

  $('input[data-role=p2p-calculator]').keyup (e)->
    target = $(e.target)
    total_amount = parseFloat(target.attr 'data-total-amount')
    total_earning = parseFloat(target.attr 'data-total-earning')
    existing = parseFloat(target.attr 'data-existing')
    amount = parseFloat(target.val()) || 0

    if amount > target.attr 'data-max'
      amount = target.attr 'data-max'
      target.val amount

    amount = parseFloat(existing) + parseFloat(amount)

    earning = ((amount / total_amount) * total_earning).toFixed(2)

    if earning < 0
      earning = 0

    earning_elements = (target.attr 'data-target').split(',')
    for earning_element, i in earning_elements
      if earning and $.isNumeric(earning)
        $(earning_element).text earning
      else
        $(earning_element).text "0.00"

  $('input[data-role=p2p-calculator]').keyup()
