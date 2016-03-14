define ['jquery'], ($)->
  calculate = (amount, rate, period, pay_method) ->
    if /等额本息/ig.test(pay_method)
      month_rate = rate / 12

      rate_pow = Math.pow(1 + month_rate, period)

      term_amount = amount * (month_rate * rate_pow) / (rate_pow-1)
      term_amount = term_amount.toFixed(2)
      result  = (term_amount * period - amount).toFixed(2)
    else if /日计息/ig.test(pay_method)
      result = amount * rate * period / 360
    else
      result = amount * rate * period / 12

    return Math.floor(result * 100) / 100

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

  $('input[data-role=fee-calculator]').keyup ()->
    $('#withdraw-input').next().text('')
  $('input[data-role=fee-calculator]').blur ()->
    checkInput()
  $('#card-select').change ()->
    checkInput()
  checkInput = () ->
    target = $('#withdraw-input')
    amount = target.val()
    $.ajax
      url: "/api/fee/"
      type: "POST"
      data: {
        card_id : $('.bindingCard').attr('id')
        amount : amount
      }
    .success (xhr)->
      target.next().text('')
      $('#card-select').next().text('')
      if xhr.ret_code > 0
        if xhr.ret_code == 30137
          $('#card-select').next().text(xhr.message)
        else
          target.next().text(xhr.message)
          target.next().show()
      else
        if (xhr.fee == 0) && (xhr.management_fee == 0 || xhr.management_fee == '0')
          strs = 0
        else if(xhr.fee != 0 && (xhr.management_fee == 0 || xhr.management_fee == '0'))
          strs = xhr.fee
        else
          strs = xhr.fee+'+'+xhr.management_fee

        $('#poundage').text(strs)
        $('#actual-amount').text(xhr.actual_amount)


  p2pCalculate = () ->
    target = $('input[data-role=p2p-calculator]')
    existing = parseFloat(target.attr 'data-existing')

    period = target.attr 'data-period'
    rate = target.attr 'data-rate'
    rate = rate/100
    pay_method = target.attr 'data-paymethod'
    activity_rate = if parseFloat(target.attr('activity-rate')) then parseFloat(target.attr('activity-rate')) else 0
    activity_jiaxi = parseFloat(target.attr('activity-jiaxi'))
    activity_rate = (activity_rate + activity_jiaxi)/100

    amount = parseFloat(target.val()) || 0

    if amount > target.attr 'data-max'
      amount = target.attr 'data-max'
      target.val amount

    amount = parseFloat(existing) + parseFloat(amount)

    earning = calculate(amount, rate, period, pay_method)
    fee_earning = calculate(amount, activity_rate, period, pay_method)
    if earning < 0
      earning = 0

    earning_elements = (target.attr 'data-target').split(',')
    fee_elements = (target.attr 'fee-target').split(',')
    for earning_element, i in earning_elements
      if earning and $.isNumeric(earning)
        $(earning_element).text earning
      else
        $(earning_element).text "0.00"

    for fee_element, i in fee_elements
      if fee_earning and $.isNumeric(fee_earning)
        $(fee_element).text fee_earning
        $('#vip-income-warp').show()
      else
        $(fee_element).text "0.00"

  $('input[data-role=p2p-calculator]').keyup (e)->
    p2pCalculate()

  $('input[data-role=p2p-calculator]').keyup()
  return {
    calculate : calculate,
    p2pCalculate :p2pCalculate,
  }
