require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'

  shim:
    'jquery.modal': ['jquery']

require ['jquery', 'jquery.modal', 'lib/backend'], ($, modal, backend)->
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
    showSpinner: true,      # Enable/disable the default spinner during AJAX requests.
    fadeDuration: 100,     # Number of milliseconds the fade transition takes (null means no transition)
    fadeDelay: 1.0          # Point during the overlay's fade-in that the modal begins to fade in (.5 = 50%, 1.5 = 150%, etc.)

  $('#order-button').click (e)->
    e.preventDefault()
    $(this).modal()

  $('#preorder_submit').click (event)->
    event.preventDefault()

    name = $('#name_input').val()
    phone = $('#phone_input').val()

    if name and phone
      backend.createPreOrder
        product_url: document.location.href
        product_type: 'trust'
        product_name: $('#product_name').text()
        user_name: name
        phone: phone
      .done ->
          alert '预约成功，稍后我们的客户经理会联系您'
          $('#name_input').val ''
          $('#phone_input').val ''
          $.modal.close()

      .fail ()->
          alert '预约失败，请稍后再试或者拨打400-9999999'

  $('#addToFavorite').click (e)->
    e.preventDefault()
    id = $(e.target).attr('data-id')
    is_favorited = $(e.target).attr('data-is-favorited')
    backend.addToFavorite e, 'trusts', id, is_favorited
