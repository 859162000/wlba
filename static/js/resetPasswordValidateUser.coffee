require.config
  paths:
    jquery: 'lib/jquery.min'
    tools: 'lib/modal.tools'

require ['jquery', 'lib/backend', 'tools'], ($, backend, tool)->
  _countDown = ()->
    element = $('#sendValidateCodeButton')
    count = 180
    $(element).prop 'disabled', true

    $('.voice').attr 'disabled','disabled'
    $('.voice-validate').attr 'disabled','disabled'
    timerFunction = ()->
      if count >= 1
        count--
        $(element).html('已经发送(' + count + ')')
        $(element).addClass("disabled")
      else
        clearInterval(intervalId)
        $(element).html('重新获取')
        $(element).prop 'disabled', false
        $(element).removeClass("disabled")
        $('.voice').removeClass('hidden')
        $('.voice-validate').removeAttr 'disabled'
        $('.voice  .reset-inner').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>')

    # Fire now and future
    timerFunction()
    intervalId = setInterval timerFunction, 1000

  $('#sendValidateCodeButton').click (event)->
    element = $('#sendValidateCodeButton')
    target = $(event.target).attr('data-url')
    $.post target
    .done ->
      $('#nextStep').prop('disabled', false)
    .fail (xhr)->
      if xhr.status > 400
        tool.modalAlert({title: '温馨提示', msg: xhr.message})
        $(element).html('重新获取')
        $(element).prop 'disabled', false
        $(element).removeClass("disabled")


    _countDown()


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
#  _countDown()

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
        count = 180
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
      if xhr.status > 400
        tool.modalAlert({title: '温馨提示', msg: xhr.message})
        $(element).html('重新获取')
        $(element).prop 'disabled', false
        $(element).removeClass("disabled")
