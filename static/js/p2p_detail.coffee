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

  $('.payment2').hide()
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
    rules:
      amount: opt
    messages:
      amount:
        required: '请输入投资金额'
        number: '请输入数字'

    errorPlacement: (error, element) ->
      error.appendTo $(element).closest('.form-row__middle').find('.form-row-error')

    success: () ->
      console.log(arguments, validator)

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

#  $(window).load (e) ->
#    if(invest_result && invest_result.length > 0)
#      $('.invest-history-table tbody').append(buildTable(invest_result.splice(0, 30)))
#      if(invest_result.length > 5)
#        $('.get-more').show()
#      else
#        $('.get-more').hide()

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
              obj = data.selectedData
              if obj.value !=''
                if $('#id_amount').val()
                  j=0
                  val_len=data2.packages.available.length
                  while j<val_len
                    if data2.packages.available[j].event_id ==7 and obj.value==data2.packages.available[j].id
                      if obj.amount !=0
                        pay_amount=$('#id_amount').val()
                        $.ajax {
                            url: '/api/redpacket/deduct/'
                            data:{
                              amount: pay_amount
                              rpa: obj.amount
                            }
                            type: 'post'
                          }
                          .done (data)->
                            $('.payment2').show()
                            $('.payment').hide()
                            $('.payment2').html(['红包使用<i>',data.deduct,'</i>元，','实际支付<i>', pay_amount-data.deduct, '</i>元'].join('')).css(color:'#999')
                            $('.payment2 i').css(
                              color: '#1A2CDB'
                            )
                      if $('#id_amount').val() - obj.invest_amount < 0
                        $('.payment2').html('投资金额未达到红包使用门槛').css(
                          color: 'red'
                        )
                        lable = $('label[for="id_amount"]')
                        if $.trim(lable.text()) == ''
                          $('label[for="id_amount"]').hide()
                    else
                      pay_amount=$('#id_amount').val()
                      pay_now = parseFloat(pay_amount)
                      pay_now =Math.round(pay_amount*100)/100
                      $('.payment i').css(
                          color: '#1A2CDB'
                        )
                      if pay_now-obj.amount<=0
                        $('.payment2').show()
                        $('.payment').hide()
                        $('.payment2').html(['红包使用<i>',pay_now,'</i>元，','实际支付<i>', 0, '</i>元'].join('')).css(color:'#999')
                        $('.payment2 i').css(
                          color: '#1A2CDB'
                        )
                      else
                        $('.payment2').show()
                        $('.payment').hide()
                        $('.payment2').html(['红包使用<i>',obj.amount,'</i>元，','实际支付<i>',pay_now-obj.amount,'</i>元，'].join('')).css(
                          color:'#999'
                        )
                        $('.payment2 i').css(
                          color: '#1A2CDB'
                        )
                    j++
                else
#                  $('.form-row-error').show()
#                  $('.form-row-error').html('请输入投资金额').css(
#                    color: 'red'
#                  )
#                  alert('请输入投资金额')
#                  window.location.href=''
              else if $('#id_amount').val()
                pay_amount=$('#id_amount').val()
                $('.payment').show()
                $('.payment2').hide()
                $('.payment').html(['实际支付<i>',pay_amount,'</i>元，'].join('')).css(
                  color:'#999'
                )
                $('.payment i').css(
                    color: '#1A2CDB'
                  )
        $('#id_amount').keyup (e) ->
          max_pay=$('#id_amount').attr('data-max')
          amount2=$('#id_amount').val()
          if obj.value
            if $('#id_amount').val()<=max_pay
              for obj in ddData
                if obj.value == $('.dd-selected-value').val()*1
                  selectedData = obj
                  break
              amount = $('#id_amount').val()
              k=0
              val_len2=data2.packages.available.length
              while k<val_len2
                if selectedData and data2.packages.available[k].event_id ==7 and obj.value==data2.packages.available[k].id
                  $('.payment2').show()
                  if amount - selectedData.invest_amount >= 0
                    pay_amount=$('#id_amount').val()
                    $.ajax {
                        url: '/api/redpacket/deduct/'
                        data:{
                          amount: pay_amount
                          rpa: obj.amount
                        }
                        type: 'post'
                      }
                      .done (data)->
                        $('.payment2').show()
                        $('.payment').hide()
                        $('.payment2').html(['红包使用<i>',data.deduct,'</i>元，','实际支付<i>', pay_amount-data.deduct, '</i>元'].join('')).css(color:'#999')
                        $('.payment2 i').css(
                          color: '#1A2CDB'
                        )
                  else if $.isNumeric(amount) and amount > 0
                    pay_amount=$('#id_amount').val()
                    $.ajax {
                        url: '/api/redpacket/deduct/'
                        data:{
                          amount: pay_amount
                          rpa: obj.amount
                        }
                        type: 'post'
                      }
                      .done (data)->
                        if pay_amount-obj.amount<=0
                          $('.payment2').show()
                          $('.payment').hide()
                          $('.payment2').html(['红包使用<i>',data.deduct,'</i>元，','实际支付<i>', pay_amount-data.deduct, '</i>元'].join('')).css(color:'#999')
                          $('.payment2 i').css(
                            color: '#1A2CDB'
                          )
                        else
                          $('.payment2').show()
                          $('.payment').hide()
                          $('.payment2').html(['红包使用<i>',obj.amount,'</i>元，','实际支付<i>',pay_amount-obj.amount,'</i>元，'].join('')).css(
                            color:'#999'
                          )
                          $('.payment2 i').css(
                            color: '#1A2CDB'
                          )
                  else
                    $('.payment2').html('投资金额未达到红包使用门槛').css(
                      color: 'red'
                    )
                    lable = $('label[for="id_amount"]')
                    if $.trim(lable.text()) == ''
                      $('label[for="id_amount"]').hide()
                else
                  if amount2
                    if amount2-obj.amount<0

                      $('.payment2').show()
                      $('.payment').hide()
                      $('.payment2').html(['红包使用<i>',amount2,'</i>元，','实际支付<i>', 0, '</i>元'].join('')).css(color:'#999')
                      $('.payment2 i').css(
                        color: '#1A2CDB'
                      )

                    else


                      amount3=$('#id_amount').val()
                      $('.invest').removeClass('notlogin')
                      if !isNaN(amount3-obj.amount)
                        $('.payment2').show()
                        $('.payment').hide()
                        $('.payment2').html(['红包使用<i>',obj.amount,'</i>元，','实际支付<i>',amount3-obj.amount,'</i>元，'].join('')).css(
                          color:'#999'
                        )
                        $('.payment2 i').css(
                          color: '#1A2CDB'
                        )
                      else
                        $('.payment2').show()
                        $('.payment').hide()
                        $('.payment2').html(['红包使用<i>',obj.amount,'</i>元，','实际支付<i>0</i>元，'].join('')).css(
                          color:'#999'
                        )
                        $('.payment2 i').css(
                          color: '#1A2CDB'
                        )
                  else
                    $('.payment2').show()
                    $('.payment').hide()
                    $('.payment2').html(['红包使用<i>0</i>元，','实际支付<i>0</i>元，'].join('')).css(
                      color:'#999'
                    )
                    $('.payment2 i').css(
                      color: '#1A2CDB'
                    )
                k++
            else
              XMLHttpRequest. readyState=0
              g=0
              obj_val=data2.packages.available.length
              while g<obj_val
                if data2.packages.available[g].event_id ==7 and obj.value==data2.packages.available[g].id
                  mes=obj.value
                g++
              if mes
                pay_amount=$('#id_amount').val()
                $.ajax {
                  url: '/api/redpacket/deduct/'
                  data:{
                    amount: pay_amount
                    rpa: obj.amount
                  }
                  type: 'post'
                }
                .done (data)->
                  $('.payment2').show()
                  $('.payment').hide()
                  $('.payment2').html(['红包使用<i>',data.deduct,'</i>元，','实际支付<i>',pay_amount-data.deduct,'</i>元，'].join('')).css(
                    color:'#999'
                  )
                  $('.payment2 i').css(
                    color: '#1A2CDB'
                  )

              else
                if amount2-obj.amount<0
                  $('.payment').hide()
                  $('.payment2').show()
                  $('.payment2').html(['红包使用<i>',amount2,'</i>元，','实际支付<i>0</i>元，'].join('')).css(color:'#999')
                  $('.payment2 i').css(
                      color: '#1A2CDB'
                  )
                else
                  $('.payment').hide()
                  $('.payment2').show()
                  $('.payment2').html(['红包使用<i>',obj.amount,'</i>元，','实际支付<i>',amount2-obj.amount,'</i>元，'].join('')).css(color:'#999')
                  $('.payment2 i').css(
                      color: '#1A2CDB'
                  )

          else
            if !isNaN($('#id_amount').val())
              pay_amount=$('#id_amount').val()
              pay_now = parseFloat(pay_amount)
              pay_now =Math.round(pay_amount*100)/100
              $('.payment i').css(
                  color: '#1A2CDB'
                )
              $('.payment2').hide()
              $('.payment').html(['实际支付<i>',pay_now,'</i>元，'].join('')).css(color:'#999')
              $('.payment i').css(
                  color: '#1A2CDB'
                )
            else
              $('.payment2').hide()
              $('.payment').html(['实际支付<i>0</i>元，'].join('')).css(color:'#999')
              $('.payment i').css(
                  color: '#1A2CDB'
                )
#          console.log($('.payment').text())


        $('#id_amount').blur (e) ->
          lable = $('label[for="id_amount"]')
          if $.trim(lable.text()) == ''
            $('label[for="id_amount"]').hide()








      return



