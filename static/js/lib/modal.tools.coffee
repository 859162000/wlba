define ['jquery', 'lib/modal'], ($, modal)->
  alert_container_id = 'alert-container-id'
  confirm_container_id = 'confirm-container-id'
  modal_container = 'modal-container'

  initAlert = () ->
    html = ['<div id= "', alert_container_id, '" class="', modal_container, '">',
            '<div class="modal-header"><span class="icon-cancel"></span></div>',
            '<div class="modal-content"><h2>购买成功</h2><p class="modal-content-inner">同志确认吗?</p></div>',
           '<div class="modal-footer"><a href="#" class="ok button-alert-ok">确认</a>',
            '</div>']
    $(html.join('')).appendTo($(document.body))
    $('#' + alert_container_id).on(modal.CLOSE, beforeClose)



  initConfirm = () ->
    html = ['<div id= "', confirm_container_id, '" class="', modal_container, '">',
            '<div class="modal-header"><span class="icon-cancel"></span></div>',
            '<div class="modal-content"><h2></h2><div class="modal-content-inner">同志确认吗?</div></div>',
           '<div class="modal-footer"><a href="#" class="ok button-confirm-ok">确认</a><a href="#" class="cancel button-confirm-cancel">取消</a></div>',
            '</div>']
    $(html.join('')).appendTo($(document.body))
    $('#' + alert_container_id).on(modal.CLOSE, beforeClose)


  beforeClose = () ->
      $('#' + confirm_container_id).off('.ok')
      $('#' + alert_container_id).off('.ok')


  init = () ->
    initAlert()
    initConfirm()


  modalAlert = (option) ->
    $('.modal-content-inner', $('#' + alert_container_id)).html(option.msg)
    $('h2', $('#' + alert_container_id)).html(option.title)
    $('#' + alert_container_id).modal()
    $('#' + alert_container_id).on 'click', '.ok', (event) ->
        $.modal.close()
        option.callback_ok && option.callback_ok.call(this, event)

    $('#' + alert_container_id).on 'click', '.icon-cancel', (event) ->
      $.modal.close()


  modalConfirm = (option) ->
    $('.modal-content-inner', $('#' + confirm_container_id)).html(option.msg)
    $('h2', $('#' + confirm_container_id)).html(option.title)
    $('#' + confirm_container_id).modal()
    $('#' + confirm_container_id).on 'click', '.ok', (event) ->
      $.modal.close()
      option.callback_ok && option.callback_ok.call(this, event)

    $('#' + confirm_container_id).on 'click', '.cancel', (event) ->
      $.modal.close()

    $('#' + confirm_container_id).on 'click', '.icon-cancel', (event) ->
      $.modal.close()

  init()

  return {
    modalAlert: modalAlert,
    modalConfirm: modalConfirm
  }
