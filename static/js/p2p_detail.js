// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min'
    }
  });

  require(['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown'], function($, _, backend, calculator, countdown) {
    return $('#purchase-form .submit-button').click(function(e) {
      var amount, captcha_0, captcha_1, product;
      e.preventDefault();
      product = $('input[name=product]').val();
      amount = $('input[name=amount]').val();
      captcha_0 = $('input[name=captcha_0]').val();
      captcha_1 = $('input[name=captcha_1]').val();
      return backend.purchaseP2P({
        product: product,
        amount: amount,
        captcha_0: captcha_0,
        captcha_1: captcha_1
      }).done(function(data) {
        alert('份额认购成功');
        return location.reload();
      }).fail(function(xhr) {
        var error_message, message, result;
        result = JSON.parse(xhr.responseText);
        message = result.message;
        error_message = '';
        if ($.type(message) === 'object') {
          error_message = _.chain(message).pairs().map(function(e) {
            return e[1];
          }).flatten().value();
        } else {
          error_message = message;
        }
        return alert(error_message);
      });
    });
  });

}).call(this);

//# sourceMappingURL=p2p_detail.map
