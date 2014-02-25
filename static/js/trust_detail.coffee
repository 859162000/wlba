require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  $ document
  .ready ->
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
        .done (data)->
            alert '预约成功，稍后我们的客户经理会联系您'
        .fail ()->
            alert '预约失败，请稍后再试或者拨打400-9999999'

