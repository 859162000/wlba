require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.placeholder': 'lib/jquery.placeholder'
    'jquery.validate': 'lib/jquery.validate.min'
    tools: 'lib/modal.tools'

  urlArgs: 'v=20151118'

  shim:
    'jquery.modal': ['jquery']
    'jquery.placeholder': ['jquery']
    'jquery.validate': ['jquery']
)

require ['jquery', 'lib/modal', 'lib/backend', 'tools', 'jquery.placeholder', 'lib/calculator', 'jquery.validate'], ($, modal, backend, tool, placeholder, validate)->
  max_amount = parseInt($('input[name=fee]').attr('data-max_amount'))
  min_amount = parseInt($('input[name=fee]').attr('data-min_amount'))
  $.validator.addMethod "balance", (value, element)->
    return backend.checkBalance(value, element)
  $.validator.addMethod "money", (value, element)->
    return backend.checkMoney(value, element)
  $.validator.addMethod "huge", (value, element)->
    return value <= max_amount
  $.validator.addMethod "small", (value, element)->
    balance = $(element).attr('data-balance')
    if value <= 0
      return false
    if balance - value == 0
      return true
    else if value >= min_amount
      return true
    return false

  $("#withdraw-form").validate
    rules:
      amount:
        required: true
        money: true
        balance: false
        huge: false
        small: false
      card_id:
        required: false
      validate_code:
        required: true
      captcha_1:
        required: true
        minlength: 1
      pwd:
        required: true

    messages:
      amount:
        required: '不能为空'
        money: '请输入正确的金额格式'
        balance: '余额不足'
        huge: '单笔提现金额不能超过' + max_amount + '万元'
        small: '最低提现金额 ' + min_amount + ' 元起。如果余额低于 ' + min_amount + ' 元，请一次性取完。'
      card_id:
        required: '请选择银行卡'
      validate_code:
        required: '请输入验证码'
      captcha_1:
        required: '不能为空'
        minlength: $.format("验证码至少输入1位")
      pwd:
        required: '请输入交易密码'

  if $('#id-is-valid').val() == 'False'
    $('#id-validate').modal()

  $('.ispan4-omega').click () ->
    $('.code-img-error').html('')
    $('#img-code-div2').modal()
    $('#img-code-div2').find('#id_captcha_1').val('')
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())
    $.getJSON url, {}, (json)->
      $('input[name="captcha_0"]').val(json.key)
      $('img.captcha').attr('src', json.image_url)

  $("#submit-code-img4").click (e) ->
    element = $('#button-get-code-btn')
    if $(element).attr 'disabled'
      return;
    phoneNumber = $(element).attr("data-phone")
    captcha_0 = $(this).parents('form').find('#id_captcha_0').val()
    captcha_1 = $(this).parents('form').find('.captcha').val()
    $.ajax
      url: "/api/phone_validation_code/" + phoneNumber + "/"
      type: "POST"
      data: {
        captcha_0 : captcha_0
        captcha_1 : captcha_1
      }
    .fail (xhr)->
      clearInterval(intervalId)
      $(element).text('重新获取')
      $(element).removeAttr 'disabled'
      $(element).addClass 'button-red'
      $(element).removeClass 'button-gray'
      result = JSON.parse xhr.responseText
      if result.type == 'captcha'
        $("#submit-code-img4").parent().parent().find('.code-img-error').html(result.message)
      else
        if xhr.status >= 400
          tool.modalAlert({title: '温馨提示', msg: result.message})
    .success ->
      element.attr 'disabled', 'disabled'
      element.removeClass 'button-red'
      element.addClass 'button-gray'
      $('.voice-validate').attr 'disabled', 'disabled'
      $.modal.close()
    intervalId
    count = 60

    $(element).attr 'disabled', 'disabled'
    $(element).addClass('disabled')
    $('.voice-validate').attr 'disabled', 'disabled'
    timerFunction = ()->
      if count >= 1
        count--
        $(element).text('重新获取(' + count + ')')
      else
        clearInterval(intervalId)
        $(element).text('重新获取')
        $(element).removeAttr 'disabled'
        $(element).removeClass('disabled')
        $(element).removeClass('button-gray')
        par = $(element).parent().parent().parent()
        par.find('.voice').removeClass('hidden')
        par.find('.voice-validate').removeAttr 'disabled'
        par.find('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>')

   # Fire now and future
    timerFunction()
    intervalId = setInterval timerFunction, 1000

  $(".voice").on 'click', '.voice-validate', (e)->
    e.preventDefault()

    if($(this).attr('disabled') && $(this).attr('disabled') == 'disabled')
      return

    element = $('.voice .span12-omega')

    url = $(this).attr('href')
    $.ajax
      url: url
      type: "POST"
      data: {
        phone: $("#button-get-code-btn").attr('data-phone').trim()
      }
    .success (json)->
      if(json.ret_code == 0)
        #TODO

        intervalId
        count = 60
        button = $("#button-get-code-btn")

        button.attr 'disabled', 'disabled'
        button.addClass 'button-gray'

        $('.voice').addClass 'tip'
        timerFunction = ()->
          if count >= 1
            count--
            element.text('语音验证码已经发送，请注意接听（' + count + '）')
          else
            clearInterval(intervalId)
            element.html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>')
            element.removeAttr 'disabled'
            button.removeAttr 'disabled'
            button.addClass 'button-red'
            button.removeClass 'button-gray'
            $('.voice').removeClass 'tip'

        # Fire now and future
        timerFunction()
        intervalId = setInterval timerFunction, 1000
      else
        #TODO
        element.html('系统繁忙请尝试短信验证码')
    .fail (xhr)->
      if xhr.status > 400
        tool.modalAlert({title: '温馨提示', msg: result.message})

  $('.poundageF').click ()->
    $('#poundageExplain').modal()
  ###显示设置密码弹框###
  $('.forget-pwd').click ()->
    tag = $(this).attr('tag')
    dr = $('.setTradingPwd1')
    if tag == '1'
      dr.find('.tag1').show()
      dr.find('.tag2').hide()
      dr.find('.nextBtn').attr('tag','1')
    else
      dr.find('.tag2').show()
      dr.find('.tag1').hide()
      dr.find('.nextBtn').attr('tag','2')
    $('#setTradingPwd').modal();
    $('.modal').css('width':'640px')
  ###判断提交表单###
  $('.withdraw-button').click ()->
    if(!$(this).hasClass('no-click'))
      if $('.bindingCard').text() == ''
        $('.bindingError').text('*请绑定银行卡')
      else
        $('#withdraw-form').submit()
  ###设置密码提交表单###
  $('#nextBtn').click ()->
    parent = $('.setTradingPwd1')
    phone = $(this).attr('data-phone')
    id = $.trim(parent.find('.sfz').val())
    select = $('#card-select1').val()
    yhkh = $.trim($('.yhkh').val())
    reg = new RegExp(/^(\d{15}$|^\d{18}$|^\d{17}(\d|X|x))$/)
    tag = $(this).attr('tag')
    $('.errorS').html('').hide()
    sfzError = parent.find('#sfzError')
    yhkError = parent.find('#yhkError')
    yhkhError = parent.find('#yhkhError')
    res = /^\d{10,20}$/
    if(id == '')
      sfzError.show().addClass('errorS').html('<i></i>请输入身份证号码')
      return
    else
      if(!reg.test(id))
        sfzError.show().addClass('errorS').html('<i></i>身份证信息有误')
        return
      else
        sfzError.show().removeClass('errorS').html('<i></i>')
    if(select == '')
      yhkError.show().addClass('errorS').html('<i></i>请输选择银行卡')
      return
    else
      yhkError.show().removeClass('errorS').html('<i></i>')
    if(yhkh == '')
      yhkhError.show().addClass('errorS').html('<i></i>请输入银行卡号')
      return
    else
      if !res.test(yhkh)
        yhkhError.show().addClass('errorS').html('<i></i>卡号无效')
        return
      else
        yhkhError.show().removeClass('errorS').html('<i></i>')

    $.ajax
      url: "/api/trade_pwd/"
      type: "POST"
      data: {
        action_type : 3
        card_id : yhkh
        citizen_id : id
        requirement_check : 1
      }
    .success (date)->
      if date.ret_code == 5
        $.modal.close()
        dr = $('.setTradingPwd2')
        if tag == '1'
          dr.find('.tag1').show()
          dr.find('.tag2').hide()
        else
          dr.find('.tag2').show()
          dr.find('.tag1').hide()
        $('#backTradingPwd').modal()
        $('#confirmBtn').attr('tag':tag)
      else
         tool.modalAlert({title: '温馨提示', msg: date.message})

  ###确认密码###
  $('#confirmBtn').click ()->
    par = $('.setTradingPwd2')
    pwd1 = $.trim(par.find('#pwd1').val())
    pwd2 = $.trim(par.find('#pwd2').val())
    erro1 = par.find('#sfzError')
    erro2 = par.find('#yzmError')
    card_id = $.trim($('.yhkh').val())
    citizen_id = $.trim($('#citizen_id').val())
    re = /^\d{6}$/
    tag = $(this).attr('tag')
    $('.errorS').html('').hide()
    if pwd1 == ''
      erro1.show().addClass('errorS').html('<i></i>请输入密码')
      return
    else
      if !re.test(pwd1)
        erro1.show().addClass('errorS').html('<i></i>格式不正确')
        return
      else
        erro1.show().removeClass('errorS').html('<i></i>')

    if pwd2 == ''
      erro2.show().addClass('errorS').html('<i></i>请输入密码')
      return
    else
      if !re.test(pwd2)
        erro2.show().addClass('errorS').html('<i></i>格式不正确')
        return
      else
        erro2.show().removeClass('errorS').html('<i></i>')
    if pwd1 != pwd2
      erro2.show().addClass('errorS').html('<i></i>交易密码不一致')
      return
    else
        erro2.show().removeClass('errorS').html('<i></i>')
    if tag == '1'
      action_type = '3'
    else
      action_type = '1'
    $.ajax
      url: "/api/trade_pwd/"
      type: "POST"
      data: {
        action_type : action_type
        card_id : card_id
        citizen_id : citizen_id
        new_trade_pwd : pwd1
        requirement_check : 0
      }
    .success ->
      location.reload()

  ###判断是否设置了交易密码###
  $.ajax
    url: "/api/profile/"
    type: "GET"
    data: {
    }
  .success (date) ->
    if date.trade_pwd_is_set
      $('.trade_pwd_is_set').show()
    else
      $('.trade_pwd_is_set_no').show()
      if date.cards_number > 0
        $('.bank-counts').show()
      else
        $('.bank-count').show()
  ###获取绑卡状态###
  $.ajax
      url: "/api/pay/the_one_card/"
      type: "GET"
      data: {
      }
    .fail ()->
      $('.noCard').show()
      $('.bindingCard').hide()
    .done (xhr) ->
      $('.noCard').hide()
      $('.bindingCard').show().text(xhr.no)
  ###绑定银行卡###
#  $('#goBindingBtn').click ->
#    $('#bindingBankBox').modal()
#    $('.modal').css('width':'640px')


