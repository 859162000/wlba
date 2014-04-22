require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.placeholder': 'lib/jquery.placeholder'

  shim:
    'jquery.modal': ['jquery']
    'jquery.placehoder': ['jquery']

require ['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder'], ($, modal, backend, placehoder)->

  $('input, textarea').placeholder()

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
