define ['jquery', 'lib/modal'], ($, modal)->
  alert_container_id = 'alert-container-id'
  confirm_container_id = 'confirm-container-id'
  modal_container = 'modal-container'
  confirmOption = null
  alertOption = null

  initAlert = () ->
    html = ['<div id= "', alert_container_id, '" class="', modal_container, '" style="display:none">',
            '<div class="modal-header"></div>',
            '<div class="modal-content"><p class="modal-content-inner">您确认吗?</p></div>',
            '<div class="modal-footer"><a href="javascript:void(0)" class="ok button-alert-ok" style="margin-right:0">确认</a>',
            '</div>']
    $(html.join('')).appendTo($(document.body))
    $('#' + alert_container_id).on 'click', '.ok', (event) ->
      $.modal.close()
      alertOption && alertOption.callback_ok && alertOption.callback_ok.call(this, event)

    $('#' + alert_container_id).on 'click', '.icon-cancel', (event) ->
      $.modal.close()

  initConfirm = () ->
    html = ['<div id= "', confirm_container_id, '" class="', modal_container, '" style="display:none">',
            '<div class="modal-header"></div>',
            '<div class="modal-content"><div class="modal-content-inner">确认吗?</div></div>',
           '<div class="modal-footer"><a href="javascript:void(0)" class="ok button-confirm-ok">确认</a><a href="javascript:void(0)" class="cancel button-confirm-cancel">取消</a></div>',
            '</div>']
    $(html.join('')).appendTo($(document.body))
    $('#' + confirm_container_id).on 'click', '.ok', (event) ->
      $.modal.close()
      confirmOption && confirmOption.callback_ok && confirmOption.callback_ok.call(this, event)

    $('#' + confirm_container_id).on 'click', '.cancel', (event) ->
      $.modal.close()

    $('#' + confirm_container_id).on 'click', '.icon-cancel', (event) ->
      $.modal.close()

  init = () ->
    initAlert()
    initConfirm()

  modalAlert = (option) ->
    alertOption = option
    $('.modal-content-inner', $('#' + alert_container_id)).html(option.msg)
    if option.title
      $('.modal-header', $('#' + alert_container_id)).html(option.title)
    else
      $('.modal-header', $('#' + alert_container_id)).css "background-color", "#fff"
    if option.btnText
      $('.button-alert-ok', $('#' + alert_container_id)).html(option.btnText)
    $('#' + alert_container_id).modal()

  modalConfirm = (option) ->
    confirmOption = option
    $('.modal-content-inner', $('#' + confirm_container_id)).html(option.msg)
    if option.title
      $('.modal-header', $('#' + confirm_container_id)).html(option.title)
    else
      $('.modal-header', $('#' + confirm_container_id)).css "background-color", "#fff"
    if option.btnText
      $('.button-confirm-ok', $('#' + confirm_container_id)).html(option.btnText)
    $('#' + confirm_container_id).modal()

  init()

  return {
    modalAlert: modalAlert,
    modalConfirm: modalConfirm
  }
