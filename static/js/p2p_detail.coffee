require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    tools: 'lib/modal.tools'
    "jquery.validate": 'lib/jquery.validate.min'
    'jquery.modal': 'lib/jquery.modal.min'
    ddslick: 'lib/jquery.ddslick'

  shims:
    "jquery.validate": ['jquery']
    "ddslick": ['jquery']

require ['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown', 'tools', 'lib/modal', "jquery.validate", 'ddslick'], ($, _, backend, calculator, countdown, tool, modal)->
  isFirst = true

  getFormatedNumber = (num) ->
    return Math.round(num*100)/100

  clearToShow = (arr) ->
    i = 0
    while arr[i] and arr.length
      if $.trim($(arr[i]).text()) == ''
        arr.splice(i, 1)
      else
        i++
    return arr

  getActualAmount = (investAmount, redpackAmount) ->
    if investAmount <= redpackAmount
      return 0
    else
      return getFormatedNumber(investAmount-redpackAmount)

  showPayInfo = (actual_payment, red_pack_payment) ->
    return ['红包使用<i class="blue">', red_pack_payment, '</i>元，实际支付<i class="blue">', actual_payment, '</i>元'].join('')
  getRedAmount = (method, red_pack_amount, event_id, highest_amount) ->
    $amount  = $('#id_amount')
    amount = $amount.val()
    if method == '*'
      final_redpack = amount * red_pack_amount
      if highest_amount && highest_amount < final_redpack
        final_redpack = highest_amount
    else
      final_redpack = red_pack_amount

    return {
      red_pack: getFormatedNumber(final_redpack)
      actual_amount: getActualAmount(amount, final_redpack)
    }


  hideEmptyLabel = (e) ->
    setTimeout (->
      lable = $('label[for="id_amount"]')
      if $.trim(lable.text()) == ''
        $('label[for="id_amount"]').hide()
    ), 10

  getRedPack = () ->
    for obj in ddData
      if obj.value == $('.dd-selected-value').val()*1
        selectedData = obj
        break
    return selectedData

  showPayTip = (method, amount) ->
    redPack = getRedPack()
    if !redPack
      return
    highest_amount = 0
    if redPack.highest_amount
      highest_amount = redPack.highest_amount
    if redPack.method == '~'
      $('#id_amount').attr('activity-jiaxi', redPack.amount*100)
      return calculator.p2pCalculate()
    else
      redPackInfo = getRedAmount(redPack.method, redPack.amount, redPack.event_id, highest_amount)
      html = showPayInfo(redPackInfo.actual_amount, redPackInfo.red_pack)
    $('.payment').html(html).show()

  $.validator.addMethod 'dividableBy100', (value, element)->
    return value % 100 == 0 && !/\./ig.test(value)
  , '请输入100的整数倍'

  $.validator.addMethod 'integer', (value, element)->
    notInteger = /\.\d*[^0]+\d*$/ig.test(value)
    return !($.isNumeric(value) && notInteger)
  , '请输入整数'

  $.validator.addMethod 'positiveNumber', (value, element)->
    return Number(value) > 0
  , '请输入有效金额'

  $.validator.addMethod 'threshold', (value, element)->
    for obj in ddData
      if obj.value == $('.dd-selected-value').val()*1
        selectedData = obj
        break
    return if selectedData then $('#id_amount').val() - selectedData.invest_amount >= 0 else true
  , '投资金额未达到理财券门槛'

  if $('#id_amount').attr('p2p-type') == '票据'
    opt =
      required: true
      number: true
      positiveNumber: true
      integer: true
      threshold: true

  else
    opt =
      required: true
      number: true
      positiveNumber: true
      dividableBy100: true
      threshold: true

  validator = $('#purchase-form').validate
    rules:
      amount: opt
    messages:
      amount:
        required: '请输入投资金额'
        number: '请输入数字'


    errorPlacement: (error, element) ->
      error.appendTo $(element).closest('.form-row__middle').find('.form-row-error')

    showErrors: (errorMap, errorList) ->
      i = 0
      while @errorList[i]
        error = @errorList[i]
        if @settings.highlight
          @settings.highlight.call this, error.element, @settings.errorClass, @settings.validClass

        @showLabel error.element, error.message
        i++

      if @errorList.length
        @toShow = @toShow.add(@containers)

      if @settings.success
        i = 0
        while @successList[i]
          @showLabel @successList[i]
          i++

      if @settings.unhighlight
        i = 0
        elements = @validElements()
        while elements[i]
          @settings.unhighlight.call this, elements[i], @settings.errorClass, @settings.validClass
          i++

      @toHide = @toHide.not(@toShow)
      @hideErrors()
      @toShow = clearToShow(@toShow)
      @addWrapper(@toShow).show()


    success: () ->
      if $('.dd-selected-value').val() != ''
        $('#purchase-form').trigger('redpack')

    highlight: (element, errorClass, validClass) ->
      if $(element).attr('id') == 'id_amount'
        $('.payment').hide()

    unhighlight: (element, errorClass, validClass) ->
      if $(element).attr('id') == 'id_amount'
        hideEmptyLabel()

    invalidHandler: (event, validator) ->
      $('.payment').hide()

    onfocusout: false

    debug: true

    submitHandler: (form)->
      #autho: hetao; time: 2014.10.11; target: 抢购时未登录状态弹出登录层
      if $('.invest').hasClass('notlogin')
        $('.login-modal').trigger('click')
        return

      tip = '您的投资金额为:' + $('input[name=amount]').val() + '元'
      tool.modalConfirm({title: '温馨提示', msg: tip, callback_ok: ()->
        product = $('input[name=product]').val()
        amount = $('input[name=amount]').val()
        redpack_id = $('.dd-selected-value').val()
#        validate_code = $('input[name=validate_code]').val()
        backend.purchaseP2P {
          product: product
          amount: amount
          redpack: redpack_id
#          validate_code: validate_code
        }
        .done (data)->

          tool.modalAlert({title: '温馨提示', msg: '份额认购成功', callback_ok: ()->
            if data.category == '酒仙众筹标'
              window.location.href="/accounts/home/jiuxian/"
            else
              window.location.href="/accounts/home"
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

  $('#purchase-form').on 'redpack', ->
    showPayTip()

  #$('#id_amount').blur hideEmptyLabel
  #$('#id_amount').keyup hideEmptyLabel

  #build the table for invest history
  buildTable = (list) ->
    html = []
    i = 0
    len = list.length

    while i < len
      html.push [
        "<tr>"
        "<td><p>"
        list[i].create_time
        "</p></td>"
        "<td><em>"
        list[i].user
        "</em></td>"
        "<td><span class='money-highlight'>"
        list[i].amount
        "</span><span>元</span></td>"
        "</tr>"
      ].join("")
      i++
    html.join ""

  page = 2
  $('.get-more').click (e) ->
    e.preventDefault()
    id = $(this).attr('data-product')
    $.post('/api/p2p/investrecord'
      p2p: id
      page: page
    ).done (data) ->
      try
        invest_result = $.parseJSON(data)
        if(invest_result && invest_result.length > 0)
          if(invest_result.length > 0)
            if(math.ceil(invest_result.length/30) < page)
              return $('.get-more').hide()
            $('.invest-history-table tbody').append(buildTable(invest_result))
            $('.get-more').show()
            page++

          else
            $('.get-more').hide()

      catch e
        $('.get-more').hide()
      return
  $(".xunlei-binding-modal").click () ->
    $('#xunlei-binding-modal').modal()

  #加息券接口
  $.post('/api/redpacket/selected/'
    product_id: $('input[name=product]').val() * 1
  ).done (data) ->
    code = data.ret_code
    if code == 0
      $('.use-jiaxi').show()
      $('.use-jiaxi-amount').text(data.amount + '% ');
      $('#id_amount').attr('activity-jiaxi', data.amount)

  ddData = []
  if $('.red-pack').size() > 0
    $(document).ready () ->
      $.post('/api/redpacket/'
        status: 'available'
        product_id: $('input[name=product]').val()
      ).done (data) ->
        availables = data.packages.available
        ddData.push(
          text: '不使用理财券'
          value: ''
          selected: true
          method: ''
          amount: 0
          invest_amount: 0
          highest_amount: 0
          event_id: 0
          description: '不使用理财券'
        )
        for obj in availables
          datetime = new Date()
          datetime.setTime(obj.unavailable_at*1000)
          available_time = [datetime.getFullYear(), datetime.getMonth() + 1, datetime.getDate()].join('-')
          highest_amount = 0

          if obj.method == '*'
            amount = obj.highest_amount
            desc = ['抵', obj.amount*100, '%投资额'].join('')
          else if obj.method == '-'
            amount = obj.amount
            desc = (if obj.invest_amount and obj.invest_amount > 0 then [obj.invest_amount, "元起用"].join('') else "无投资门槛")
          else
            amount = ''
            desc = (if obj.invest_amount and obj.invest_amount > 0 then [obj.invest_amount, "元起用"].join('') else "无投资门槛")


          if obj.highest_amount
            highest_amount = obj.highest_amount
            
          if obj.method == '~'
            text = [obj.name, ' 加息', Number((obj.amount * 100).toFixed(3)), '%'].join('')
            imageSrc = '/static/imgs/pc/p2p_detail/icon_jiaxi.png';
          else
            text = [obj.name, ' ', amount, '元'].join('')
            imageSrc = '/static/imgs/pc/p2p_detail/icon_redpack.png';

          ddData.push(
            text: text
            value: obj.id
            method: obj.method
            selected: false
            amount: obj.amount
            invest_amount: obj.invest_amount
            event_id: obj.event_id
            highest_amount: highest_amount
            description: desc + ', ' + available_time + '过期'
            imageSrc: imageSrc
          )
        $('.red-pack').ddslick
          data: ddData
          width: 194
          imagePosition: "right"
          selectText: "请选择理财券"
          onSelected: (data) ->
            if validator.checkForm() && $('.dd-selected-value').val() != ''
              $('#purchase-form').trigger('redpack')
            else
              $('.payment').hide()


            if validator.checkForm() && $('.dd-selected-value').val() != '' && data.selectedData.method == '~'
               $('.payment').hide()
            else
              $('#id_amount').attr('activity-jiaxi', 0)
              calculator.p2pCalculate()

            if !isFirst
              $('#purchase-form').valid()
              hideEmptyLabel()
            isFirst = false

      return
