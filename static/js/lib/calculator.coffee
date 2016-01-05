define ['jquery'], ($)->
  calculate = (amount, rate, period, pay_method) ->
    if /等额本息/ig.test(pay_method)
      rate_pow = Math.pow(1 + rate, period)
      divisor = rate_pow - 1
      term_amount = amount * (rate * rate_pow) / divisor
      result  = term_amount * period - amount
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

    ###fee_element = target.attr 'data-target-fee'
    actual_element = target.attr 'data-target-actual'
    fee_switch = target.attr 'data-switch'
    fee_interval = target.attr 'data-interval'
    fee_count = target.attr 'data-count'
    fee_poundage = target.attr 'data-poundage'
    data_balance = target.attr 'data-balance'
    uninvested = $('input[name=uninvested]').val()
    arrays = eval(fee_interval)
    if fee_switch == 'on'
      if amount != ''
        if fee_count > 2
          for array , i in arrays
            if amount > arrays[i][0] && amount <= arrays[i][1]
              sxf = arrays[i][2]
          if sxf == undefined
            sxf = 5
        else
          sxf = 0
      else
         sxf = 0

      m = data_balance - amount
      if m >= uninvested
        zjglf = 0
      else
        zjglf = Math.abs(uninvested - m)*rate

      fee = (sxf+zjglf).toFixed(2)
      actual = (amount - fee).toFixed(2)
      if actual < 0
        actual=0
      if fee and $.isNumeric(fee)
        $(fee_element).text fee
      else
        $(fee_element).text "0.00"

      if actual and $.isNumeric(actual)
        $(actual_element).text actual
      else
        $(actual_element).text "0.00"

      if sxf == 0 &&  zjglf == 0
        str = '0'
      else
        if sxf == 0
          sxf_str = '0'
        else
          sxf_str = sxf

        if zjglf == 0
          zjglf_str = ''
        else
          zjglf_str = zjglf.toFixed(2)
        if zjglf_str == ''
          str = sxf_str
        else
          str = sxf_str + '+' +zjglf_str
      $(fee_poundage).text str###

  ######$('input[data-role=fee-calculator]').keyup()

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

