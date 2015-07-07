// Generated by CoffeeScript 1.8.0
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
      count = 180;
      $(element).prop('disabled', true);
      $('.voice').attr('disabled', 'disabled');
      $('.voice-validate').attr('disabled', 'disabled');
      timerFunction = function() {
        if (count >= 1) {
          count--;
          $(element).html('已经发送(' + count + ')');
          return $(element).addClass("disabled");
        } else {
          clearInterval(intervalId);
          $(element).html('重新获取');
          $(element).prop('disabled', false);
          $(element).removeClass("disabled");
          $('.voice').removeClass('hidden');
          $('.voice-validate').removeAttr('disabled');
          return $('.voice  .reset-inner').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>');
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    };
    $('#sendValidateCodeButton').click(function(event) {
      var target;
      target = $(event.target).attr('data-url');
      $.post(target).done(function() {
        return $('#nextStep').prop('disabled', false);
      }).fail(function(xhr) {
        if (xhr.status > 400) {
          return tool.modalAlert({
            title: '温馨提示',
            msg: result.message,
            callback_ok: _showModal
          });
        }
      });
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
      }).done(function() {
        return window.location = '/accounts/password/reset/set_password/';
      }).fail(function() {
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
    return $(".voice").on('click', '.voice-validate', function(e) {
      var element, url;
      e.preventDefault();
      if ($(this).attr('disabled') && $(this).attr('disabled') === 'disabled') {
        return;
      }
      element = $('.voice .reset-inner');
      url = $(this).attr('href');
      return $.ajax({
        url: url,
        type: "POST",
        data: {
          phone: /\d{11}/ig.exec($("#sendValidateCodeButton").attr('data-phone').trim())[0]
        }
      }).success(function(json) {
        var button, count, intervalId, timerFunction;
        if (json.ret_code === 0) {
          intervalId;
          count = 180;
          button = $("#sendValidateCodeButton");
          button.attr('disabled', 'disabled');
          $('.voice').addClass('tip');
          timerFunction = function() {
            if (count >= 1) {
              count--;
              return element.text('语音验证码已经发送，请注意接听（' + count + '）');
            } else {
              clearInterval(intervalId);
              element.html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>');
              element.removeAttr('disabled');
              button.removeAttr('disabled');
              button.addClass('button-red');
              button.removeClass('button-gray');
              return $('.voice').removeClass('tip');
            }
          };
          timerFunction();
          return intervalId = setInterval(timerFunction, 1000);
        } else {
          return element.html('系统繁忙请尝试短信验证码');
        }
      }).fail(function(xhr) {
        if (xhr.status > 400) {
          return tool.modalAlert({
            title: '温馨提示',
            msg: result.message,
            callback_ok: _showModal
          });
        }
      });
    });
  });

}).call(this);

//# sourceMappingURL=resetPasswordValidateUser.js.map
