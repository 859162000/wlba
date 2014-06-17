define ['jquery', 'jquery.modal'], ($, modal)->
  $.modal.defaults =
    overlay: "#000",
    opacity: 0.6,
    zIndex: 99,
    escapeClose: true,
    clickClose: true,
    closeText: 'Close',
    closeClass: '',
    modalClass: "modal",
    spinnerHtml: null,
    showSpinner: true,
    showClose: true,
    fadeDuration: null,   # Number of milliseconds the fade animation takes.
    fadeDelay: 1.0