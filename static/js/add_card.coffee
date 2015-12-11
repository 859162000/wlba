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

  $('#select_bank').focus ->
      $('#select_bank').addClass('selected');
  $('#select_bank').blur ->
      if($(this).val() == '')
        $('#select_bank').removeClass('selected');
  $('#goPersonalInfo').click ->
    bank = $('#select_bank')
    card = $('#cardId')
    if(bank.val() == '')
      bank.next().html('<i class="cha"></i>请选择银行')
      return
    else
      bank.next().html('<i class="dui"></i>')

    if(card.val() == '')
      card.next().html('<i class="cha"></i>请输入卡号')
      return
    else
      re = /^\d{10,20}$/
      if !re.test(card.val().replace(/[ ]/g,""))
        card.next().html('<i class="cha"></i>输入的卡号有误')
        return
      else
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
        .done ()->
          console.log('11111')
        .fail (xhr)->
          result = JSON.parse xhr.responseText
          if result.error_number == 5
            tool.modalAlert({title: '温馨提示', msg: result.message})
            return
          tool.modalAlert({title: '温馨提示', msg: '添加银行卡失败'})



  $("#cardId").keydown ->
       value = $(this).val().replace(/\s/g,'').replace(/(\d{4})(?=\d)/g,"$1 ");
       $(this).val(value)

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
    $(this).modal()

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


