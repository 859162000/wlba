(function() {
  define(['jquery', 'lib/modal'], function($, modal) {
    var alertOption, alert_container_id, confirmOption, confirm_container_id, init, initAlert, initConfirm, modalAlert, modalConfirm, modal_container;
    alert_container_id = 'alert-container-id';
    confirm_container_id = 'confirm-container-id';
    modal_container = 'modal-container';
    confirmOption = null;
    alertOption = null;
    initAlert = function() {
      var html;
      html = ['<div id= "', alert_container_id, '" class="', modal_container, '" style="display:none">', '<div class="modal-header"></div>', '<div class="modal-content"><p class="modal-content-inner">您确认吗?</p></div>', '<div class="modal-footer"><a href="#" class="ok button-alert-ok">确认</a>', '</div>'];
      $(html.join('')).appendTo($(document.body));
      $('#' + alert_container_id).on('click', '.ok', function(event) {
        $.modal.close();
        return alertOption && alertOption.callback_ok && alertOption.callback_ok.call(this, event);
      });
      return $('#' + alert_container_id).on('click', '.icon-cancel', function(event) {
        return $.modal.close();
      });
    };
    initConfirm = function() {
      var html;
      html = ['<div id= "', confirm_container_id, '" class="', modal_container, '" style="display:none">', '<div class="modal-header"></div>', '<div class="modal-content"><div class="modal-content-inner">确认吗?</div></div>', '<div class="modal-footer"><a href="#" class="ok button-confirm-ok">确认</a><a href="#" class="cancel button-confirm-cancel">取消</a></div>', '</div>'];
      $(html.join('')).appendTo($(document.body));
      $('#' + confirm_container_id).on('click', '.ok', function(event) {
        $.modal.close();
        return confirmOption && confirmOption.callback_ok && confirmOption.callback_ok.call(this, event);
      });
      $('#' + confirm_container_id).on('click', '.cancel', function(event) {
        return $.modal.close();
      });
      return $('#' + confirm_container_id).on('click', '.icon-cancel', function(event) {
        return $.modal.close();
      });
    };
    init = function() {
      initAlert();
      return initConfirm();
    };
    modalAlert = function(option) {
      alertOption = option;
      $('.modal-content-inner', $('#' + alert_container_id)).html(option.msg);
      if (option.title) {
        $('.modal-header', $('#' + alert_container_id)).html(option.title);
      } else {
        $('.modal-header', $('#' + alert_container_id)).css("background-color", "#fff");
      }
      if (option.btnText) {
        $('.button-alert-ok', $('#' + alert_container_id)).html(option.btnText);
      }
      return $('#' + alert_container_id).modal();
    };
    modalConfirm = function(option) {
      confirmOption = option;
      $('.modal-content-inner', $('#' + confirm_container_id)).html(option.msg);
      if (option.title) {
        $('.modal-header', $('#' + confirm_container_id)).html(option.title);
      } else {
        $('.modal-header', $('#' + confirm_container_id)).css("background-color", "#fff");
      }
      if (option.btnText) {
        $('.button-confirm-ok', $('#' + confirm_container_id)).html(option.btnText);
      }
      return $('#' + confirm_container_id).modal();
    };
    init();
    return {
      modalAlert: modalAlert,
      modalConfirm: modalConfirm
    };
  });
}).call(this);
