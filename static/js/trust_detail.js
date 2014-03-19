// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery', 'lib/backend'], function($, backend) {
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
        }).done(function(data) {
          return alert('预约成功，稍后我们的客户经理会联系您');
        }).fail(function() {
          return alert('预约失败，请稍后再试或者拨打400-9999999');
        });
      }
    });
    return $('#addToFavorite').click(function(e) {
      var id;
      e.preventDefault();
      id = $(e.target).attr('data-id');
      return backend.addToFavorite('trusts', id);
    });
  });

}).call(this);

//# sourceMappingURL=trust_detail.map
