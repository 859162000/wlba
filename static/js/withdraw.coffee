require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.placeholder': 'lib/jquery.placeholder'
    'jquery.validate': 'lib/jquery.validate.min'
    tools: 'lib/modal.tools'

  shim:
    'jquery.modal': ['jquery']
    'jquery.placeholder': ['jquery']
    'jquery.validate': ['jquery']
)

require ['jquery', 'lib/modal', 'lib/backend', 'tools', 'jquery.placeholder', 'lib/calculator', 'jquery.validate'], ($, modal, backend, tool, placeholder, validate)->

  $.validator.addMethod "balance", (value, element)->
    return backend.checkBalance(value, element)
  $.validator.addMethod "money", (value, element)->
    return backend.checkMoney(value, element)
  $.validator.addMethod "huge", (value, element)->
    return value <= 50000
  $.validator.addMethod "small", (value, element)->
    balance = $(element).attr('data-balance')
    if value <= 0
      return false
    if balance - value == 0
      return true
    else if value >= 50
      return true
    return false

  $("#withdraw-form").validate
    rules:
      amount:
        required: true
        money: true
        balance: true
        huge: true
        small: true
      card_id:
        required: true
      validate_code:
        required: true
      captcha_1:
        required: true
        minlength: 1

    messages:
      amount:
        required: '不能为空'
        money: '请输入正确的金额格式'
        balance: '余额不足'
        huge: '提现金额不能超过50000'
        small: '最低提现金额 50 元起。如果余额低于 50 元，请一次性取完。'
      card_id:
        required: '请选择银行卡'
      validate_code:
        required: '请输入验证码'
      captcha_1:
        required: '不能为空'
        minlength: $.format("验证码至少输入1位")

  if $('#id-is-valid').val() == 'False'
    $('#id-validate').modal()

  $('#button-get-code-btn').click () ->
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
        $("#submit-code-img1").parent().parent().find('.code-img-error').html(result.message)
      else
        if xhr.status >= 400
          tool.modalAlert({title: '温馨提示', msg: result.message})
    .success ->
      element.attr 'disabled', 'disabled'
      element.removeClass 'button-red'
      element.addClass 'button-gray'
      $('.voice-validate').attr 'disabled', 'disabled'

    intervalId
    count = 180

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
        $('.voice').removeClass('hidden')
        $('.voice-validate').removeAttr 'disabled'
        $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>')

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
        phone: $("#button-get-validate-code").attr('data-phone').trim()
      }
    .success (json)->
      if(json.ret_code == 0)
        #TODO

        intervalId
        count = 180
        button = $("#button-get-validate-code")

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
