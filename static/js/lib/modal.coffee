define ['jquery', 'jquery.modal'], ($, modal)->
  $.modal.defaults =
    overlay: "#000",        # Overlay color
    opacity: 0,          # Overlay opacity
    zIndex: 1,              # Overlay z-index.
    escapeClose: true,      # Allows the user to close the modal by pressing `ESC`
    clickClose: true,       # Allows the user to close the modal by clicking the overlay
    closeText: 'Close',     # Text content for the close <a> tag.
    closeClass: '',         # Add additional class(es) to the close <a> tag.
    showClose: false,       # Shows a (X) icon/link in the top-right corner
    modalClass: "modal",    # CSS class added to the element being displayed in the modal.
    spinnerHtml: null,      # HTML appended to the default spinner during AJAX requests.
