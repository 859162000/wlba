(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      tools: 'lib/modal.tools'
    }
  });
  require(['jquery', 'lib/backend', 'tools'], function($, backend, tool) {
    var _countDown;
    _countDown = function() {
      var count, element, intervalId, timerFunction;
      element = $('#sendValidateCodeButton');
      count = 60;
      $(element).prop('disabled', true);
      timerFunction = function() {
        if (count >= 1) {
          count--;
          $(element).html('已经发送(' + count + ')');
          return $(element).addClass("disabled");
        } else {
          clearInterval(intervalId);
          $(element).html('重新获取');
          $(element).prop('disabled', false);
          return $(element).removeClass("disabled");
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    };
    $('#sendValidateCodeButton').click(function(event) {
      var target;
      target = $(event.target).attr('data-url');
      $.post(target.done(function() {
        return $('#nextStep').prop('disabled', false);
      }));
      return _countDown();
    });
    $('#nextStep').click(function(e) {
      var target, validate_code;
      target = $(e.target).attr('data-url');
      validate_code = $('input[name="validate_code"]').val();
      if (validate_code === '') {
        tool.modalAlert({
          title: '温馨提示',
          msg: '验证码不能为空'
        });
        return;
      }
      return $.post(target, {
        "validate_code": validate_code
      }.done(function() {
        return window.location = '/accounts/password/reset/set_password/';
      })).fail(function() {
        return tool.modalAlert({
          title: '温馨提示',
          msg: '验证失败!'
        });
      });
    });
    $('#validate_form').on('submit', function(e) {
      e.preventDefault();
      return $('#nextStep').click();
    });
    return _countDown();
  });
}).call(this);
