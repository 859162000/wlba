(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'jquery.placeholder': 'lib/jquery.placeholder'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.placeholder': ['jquery']
    }
  });
  require(['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder'], function($, modal, backend, placeholder) {
    $('input, textarea').placeholder();
    $('#order-button').click(function(e) {
      e.preventDefault();
      return $(this).modal();
    });
    $('.order-button').click(function(e) {
      e.preventDefault();
      return $(this).modal();
    });
    $('#preorder_submit').click(function(event) {
      var name, phone;
      event.preventDefault();
      name = $('#name_input').val();
      phone = $('#phone_input').val();
      if (name && phone) {
        return backend.createPreOrder({
          product_url: document.location.href,
          product_type: 'trust',
          product_name: $('#product_name').text(),
          user_name: name,
          phone: phone
        }).done(function() {
          alert('预约成功，稍后我们的客户经理会联系您');
          $('#name_input').val('');
          $('#phone_input').val('');
          return $.modal.close();
        }).fail(function() {
          return alert('预约失败，请稍后再试或者拨打400-9999999');
        });
      }
    });
    return $('#addToFavorite').click(function(e) {
      e.preventDefault();
      return backend.addToFavorite(e.target, 'trusts');
    });
  });
}).call(this);
