require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    tools: 'lib/modal.tools'
    "jquery.validate": 'lib/jquery.validate.min'
    'jquery.modal': 'lib/jquery.modal.min'
    ddslick: 'lib/jquery.ddslick.min'

  shims:
    "jquery.validate": ['jquery']
    "ddslick": ['jquery']

require ['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown', 'tools', 'lib/modal', "jquery.validate", 'ddslick'], ($, _, backend, calculator, countdown, tool, modal)->

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
  , '投资金额未达到红包使用门槛'

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
    debug: true
    rules:
      amount: opt
    messages:
      amount:
        required: '请输入投资金额'
        number: '请输入数字'

    errorPlacement: (error, element) ->
      error.appendTo $(element).closest('.form-row__middle').find('.form-row-error')

    success: () ->
      $('#purchase-form').trigger('redpack')

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
    console.log('hello', 'redpack')


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

  ddData = []
  if $('.red-pack').size() > 0
    $(document).ready () ->
      $.post('/api/redpacket/'
        status: 'available'
      ).done (data) ->
        data2=data
        availables = data.packages.available
        ddData.push(
          text: '不使用红包'
          value: ''
          selected: true
          amount: 0
          invest_amount: 0
          description: '不使用红包'
        )
        for obj in availables
          desc = (if obj.invest_amount and obj.invest_amount > 0 then "投资" + obj.invest_amount + "元可用" else "无投资门槛")
          datetime = new Date()
          datetime.setTime(obj.unavailable_at*1000)
          available_time = [datetime.getFullYear(), datetime.getMonth() + 1, datetime.getDate()].join('-')
          ddData.push(
            text: obj.name
            value: obj.id
            selected: false
            amount: obj.amount
            invest_amount: obj.invest_amount
            description: desc + ', ' + available_time + '过期'
          )
        $('.red-pack').ddslick
          data: ddData
          width: 194
          imagePosition: "left"
          selectText: "请选择红包"
          onSelected: (data) ->
              console.log(validator.checkForm(), 'hello')
              if validator.checkForm()
                $('#purchase-form').trigger('redpack')
              else
                $('#purchase-form').valid()



        $('#id_amount').keyup (e) ->
          console.log('hello')


        $('#id_amount').blur (e) ->
          lable = $('label[for="id_amount"]')
          if $.trim(lable.text()) == ''
            $('label[for="id_amount"]').hide()








      return



