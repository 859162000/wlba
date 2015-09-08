require.config
  paths:
    jquery: 'lib/jquery.min'
    tools: 'lib/modal.tools'
    'jquery.modal' : 'lib/jquery.modal.min'

require ['jquery', 'lib/backend', 'tools'], ($, backend, tool)->
  $('.captcha-refresh').click ->
    $form = $(this).parents('form')
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())
    $.getJSON url, {}, (json)->
      $form.find('input[name="captcha_0"]').val(json.key)
      $form.find('img.captcha').attr('src', json.image_url)

  $('#sendValidateCodeButton').click ()->
    $('#img-code-div2').modal()
    $('#img-code-div2').find('#id_captcha_1').val('')
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())
    $.getJSON url, {}, (json)->
      $('input[name="captcha_0"]').val(json.key)
      $('img.captcha').attr('src', json.image_url)

  $("#submit-code-img4").click () ->
    element = $('#sendValidateCodeButton')
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
    .fail (xhr) ->
      clearInterval(intervalId)
      $(element).text('重新获取')
      $(element).removeAttr 'disabled'
      if (xhr.status >= 400)
        result = JSON.parse xhr.responseText
        tool.modalAlert({
          title: '温馨提示',
          msg: result.message
        });
        $(element).html('重新获取');
        $(element).prop('disabled', false);
        $(element).removeClass("disabled");
    .success ->
      element.attr 'disabled', 'disabled'
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
        $('.voice').removeClass('hidden')
        $('.voice-validate').removeAttr 'disabled'
        $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>')

    timerFunction()
    intervalId = setInterval timerFunction, 1000


  $('#nextStep').click (e)->
    # Check the validate code first
    target = $(e.target).attr('data-url')
    validate_code = $('input[name="validate_code"]').val()

    if validate_code == ''
      tool.modalAlert({title: '温馨提示', msg: '验证码不能为空'})
      return

    $.post target, {
        "validate_code": validate_code
      }
      .done ->
        # If succeeded, then go to password setting page
        window.location = '/accounts/password/reset/set_password/'
      .fail ->
        tool.modalAlert({title: '温馨提示', msg: '验证失败!'})

  $('#validate_form').on 'submit', (e) ->
    e.preventDefault()
    $('#nextStep').click()


  $(".voice").on 'click', '.voice-validate', (e)->
    e.preventDefault()

    if($(this).attr('disabled') && $(this).attr('disabled') == 'disabled')
      return

    element = $('.voice .reset-inner')

    url = $(this).attr('href')
    $.ajax
      url: url
      type: "POST"
      data: {
        phone: /\d{11}/ig.exec($("#sendValidateCodeButton").attr('data-phone').trim())[0]
      }
    .success (json)->
      if(json.ret_code == 0)
        #TODO

        intervalId
        count = 60
        button = $("#sendValidateCodeButton")

        button.attr 'disabled', 'disabled'

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
      element = $('#sendValidateCodeButton')
      if xhr.status >= 400
        tool.modalAlert({title: '温馨提示', msg: xhr.message})
        $(element).html('重新获取')
        $(element).prop 'disabled', false
        $(element).removeClass("disabled")
