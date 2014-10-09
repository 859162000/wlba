(function() {
  define(['jquery', 'jquery.modal'], function($, modal) {
    return $.modal.defaults = {
      overlay: "#000",
      opacity: 0.6,
      zIndex: 99,
      escapeClose: true,
      clickClose: false,
      closeText: '×',
      closeClass: '',
      modalClass: "modal",
      spinnerHtml: "",
      showSpinner: true,
      showClose: true,
      fadeDuration: null,
      fadeDelay: 1.0
    };
  });
}).call(this);
