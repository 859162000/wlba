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

require ['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder', 'jquery.validate', 'tools'], ($, modal, backend, placeholder, validate, tool)->
  url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())
  $.getJSON url, {}, (json)->
    $('#withdraw-form').find('input[name="captcha_0"]').val(json.key)
    $('#withdraw-form').find('img.captcha').attr('src', json.image_url)

  $('input, textarea').placeholder()

  ###选择银行卡下拉框###
  $('.select_bank').focus ->
      $('.select_bank').addClass('selected');
  $('.select_bank').blur ->
      if($(this).val() == '')
        $('.select_bank').removeClass('selected');

  ###提交银行卡信息###
  $('#goPersonalInfo').click ->
    par = $(this).parent().parent()
    bank = par.find('.select_bank')
    card = par.find('.cardId')
    if _checkBankCard(bank,card)
      card.next().html('<i class="dui"></i>')
      $.ajax {
        url: '/api/card/'
        data: {
          no: card.val().replace(/[ ]/g,"")
          bank: bank.val()
          is_default: false
        }
        type: 'post'
      }
      .done (data)->
        par.find('.bankName').text(data.bank_name+'（储蓄卡）')
        par.find('.bankId').text(data.no.replace(/\s/g,'').replace(/(\d{4})(?=\d)/g,"$1 "))
        $('#confirmInfo').show()
        $('#chooseBank,.bankTitle span').hide()
      .fail (xhr)->
        result = JSON.parse xhr.responseText
        if result.error_number == 5
          tool.modalAlert({title: '温馨提示', msg: result.message})
          return
        tool.modalAlert({title: '温馨提示', msg: '添加银行卡失败'})

  ###验证银行卡信息###
  _checkBankCard = (bank,card)->
    checkIsOrNo = false
    if(bank.val() == '')
      bank.next().html('<i class="cha"></i>请选择银行')
      checkIsOrNo = false
    else
      bank.next().html('<i class="dui"></i>')
      checkIsOrNo = true

    if(card.val() == '')
      card.next().html('<i class="cha"></i>请输入卡号')
      checkIsOrNo = false
    else
      re = /^\d{10,20}$/
      if !re.test(card.val().replace(/[ ]/g,""))
        card.next().html('<i class="cha"></i>输入的卡号有误')
        checkIsOrNo = false
      else
       card.next().html('<i class="dui"></i>')
       checkIsOrNo = true
    return checkIsOrNo

  ###个人信息###
  $('#bindingBtn').click ->
    btns = $('#bindingBtn')
    _checkPerInfo(btns)

  ###验证个人信息###
  _checkPerInfo = (btns)->
    bankPhone = btns.parent().parent().find('.bankPhone')
    code = btns.parent().parent().find('.code')
    if !_checkMobile(bankPhone)
      return
    else
      if(code.val() == '')
        code.parent().find('span').html('<i class="cha"></i>请填写验证码')
        return
      else
         code.parent().find('span').html('<i class="dui"></i>')
         $.ajax {
            url: ''
            data: {
            }
            type: 'post'
          }
          .done ()->
            console.log('11111')
          .fail (xhr)->
            console.log('222222')

  $('#withdrawBindingBtn').click ->
    par = $(this).parent().parent()
    bank = par.find('.select_bank')
    card = par.find('.cardId')
    btn = $('#withdrawBindingBtn')
    _checkBankCard(bank,card)
    _checkPerInfo(btn)

  $('.bankPhone').blur ->
     if _checkMobile($(this))
       $('.get-code').addClass('go-get-code')
     else
       $('.get-code').removeClass('go-get-code')

  ###验证手机号###
  _checkMobile = (bankPhone)->
    checkIsNo = false
    re = /^1\d{10}$/
    identifier = bankPhone.val()
    if(identifier == '')
      bankPhone.next().html('<i class="cha"></i>请填写手机号')
      checkIsNo = false
    else
      if !re.test(identifier)
        bankPhone.next().html('<i class="cha"></i>格式不正确')
        checkIsNo = false
      else
        bankPhone.next().html('<i class="dui"></i>')
        checkIsNo = true
    return checkIsNo

  ###银行卡格式###
  $(".cardId").keydown ->
       value = $(this).val().replace(/\s/g,'').replace(/(\d{4})(?=\d)/g,"$1 ");
       $(this).val(value)

  ###图片验证码###
  $('.codeBox').delegate('.go-get-code','click', ->
    $('.code-img-error').html('')
    $('#img-code-div2').modal()
    $('#img-code-div2').find('#id_captcha_1').val('')
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())
    $.getJSON url, {}, (json)->
      $('input[name="captcha_0"]').val(json.key)
      $('img.captcha').attr('src', json.image_url)
  )

  ###短信验证码###
  $("#submit-code-img4").click (e) ->
    element = $('.get-code')
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
      $(element).addClass 'go-get-code'
      result = JSON.parse xhr.responseText
      if result.type == 'captcha'
        $("#submit-code-img4").parent().parent().find('.code-img-error').html(result.message)
      else
        if xhr.status >= 400
          tool.modalAlert({title: '温馨提示', msg: result.message})
    .success ->
      element.attr 'disabled', 'disabled'
      element.removeClass 'go-get-code'
      $.modal.close()
    intervalId
    count = 60

    $(element).attr 'disabled', 'disabled'
    timerFunction = ()->
      if count >= 1
        count--
        $(element).text('重新获取(' + count + ')')
      else
        clearInterval(intervalId)
        $(element).text('重新获取')
        $(element).removeAttr 'disabled'

   # Fire now and future
    timerFunction()
    intervalId = setInterval timerFunction, 1000
  ###绑定银行卡###
  $('.binding-card').click ->
    $('#bindingOldCard').modal()
    $('#bindingOldCard').find('.close-modal').hide()
    $('.modal').css('width':'560px')
    par = $(this).parent()
    card = par.find('.bank-card--info-value').text()
    str = par.find('.bankname').attr('title')+'尾号'+card.substr(card.length-4)
    $('.bankInfo').html(str)

  ###确认绑定###
  $('.ok-btn').click ->
    $.ajax {
      url: ''
      data: {
      }
      type: 'post'
    }
    .done ()->
      location.reload()
    .fail (xhr)->
      console.log('222222')
  ###取消绑定###
  $('.no-btn').click ->
    $.modal.close()


  $('.change-bank').click ->
    $('#confirmInfo').hide()
    $('#chooseBank,.bankTitle span').show()

  $('.captcha-refresh').click ->
    $form = $(this).parents('form')
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())

    $.getJSON url, {}, (json)->
      $form.find('input[name="captcha_0"]').val(json.key)
      $form.find('img.captcha').attr('src', json.image_url)

  $('#add-card-button').click (e)->
    if $('#id-is-valid').val() == 'False'
      $('#id-validate').modal()
      return
    e.preventDefault()
#    $(this).modal()
    $('.banks-list,.bankManage').hide()
    $('#chooseBank,.bankTitle').show()

  _showModal = ()->
    $('#add-card-button').modal()

  $('#add-card').click (e)->
    e.preventDefault()
    card_no = $('#card-no').val()
    if !backend.checkCardNo(card_no)
      tool.modalAlert({title: '温馨提示', msg: '请输入有效的银行卡号', callback_ok: _showModal})
      return

    bank_id = $('#bank-select').val()
    if !bank_id
      tool.modalAlert({title: '温馨提示', msg: '请选择银行', callback_ok: _showModal})
      return

    is_default = $('#default-checkbox').prop('checked')
    $.ajax {
      url: '/api/card/'
      data: {
        no: card_no
        bank: bank_id
        is_default: is_default
      }
      type: 'post'
    }
    .done ()->
      location.reload()
    .fail (xhr)->
      $.modal.close()
      result = JSON.parse xhr.responseText
      if result.error_number == 5
        tool.modalAlert({title: '温馨提示', msg: result.message})
        return
      tool.modalAlert({title: '温馨提示', msg: '添加银行卡失败'})

  card_id = ""
  $('a#del-card').click (e)->
    card_id = $(this).attr("card_id")
    tool.modalConfirm({title: '温馨提示', msg: '确定删除？', callback_ok: _delCard})

  _delCard = ()->
    $.ajax {
      url: '/api/card/' + card_id + '/'
      data: {
        card_id: card_id
      }
      type: 'delete'
    }
    .done ()->
      location.reload()
    .fail (xhr)->
      $.modal.close()
      result = JSON.parse xhr.responseText
      if result.error_number == 5
        tool.modalAlert({title: '温馨提示', msg: result.message})
        return
      tool.modalAlert({title: '温馨提示', msg: '删除失败'})


