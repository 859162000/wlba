// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery', 'lib/backend'], function($, backend) {
    var Request, checkMobile, promo_token;
    Request = new Object();
    Request = backend.getRequest();
    promo_token = Request['promo_token'];
    if (promo_token) {
      $("#reg_invitecode").val(promo_token);
    }
    checkMobile = function(identifier) {
      var re;
      re = void 0;
      re = /^1\d{10}$/;
      return re.test(identifier);
    };
    $("#button-get-validate-code-modal").click(function(e) {
      var count, element, intervalId, phoneNumber, timerFunction;
      element = this;
      if ($(element).hasClass('disable')) {
        return;
      }
      $(".error-message").text("");
      phoneNumber = $("#reg_identifier").val().trim();
      if (checkMobile(phoneNumber)) {
        $.ajax({
          url: "/api/phone_validation_code/register/" + phoneNumber + "/",
          type: "POST"
        }).fail(function(xhr) {
          var result;
          clearInterval(intervalId);
          $(element).text('重新获取');
          $(element).removeClass('disable');
          result = JSON.parse(xhr.responseText);
          return $(".error-message").text(result.message);
        });
        intervalId;
        count = 60;
        $(element).addClass('disable');
        timerFunction = function() {
          if (count >= 1) {
            count--;
            return $(element).text('重新获取(' + count + ')');
          } else {
            clearInterval(intervalId);
            $(element).text('重新获取');
            return $(element).removeClass('disable');
          }
        };
        timerFunction();
        return intervalId = setInterval(timerFunction, 1000);
      } else {
        return $(".error-message").text("手机号输入错误");
      }
    });
    return $("#register_submit").click(function(e) {
      var element, identifier, invite_code, validate_code;
      element = this;
      if ($(element).hasClass("disable")) {
        return;
      }
      $(".error-message").text("");
      identifier = $("#reg_identifier").val().trim();
      if (!checkMobile(identifier)) {
        $(".error-message").text("手机号输入错误");
        return;
      }
      validate_code = $("#id_validate_code").val().trim();
      if (validate_code.length !== 6) {
        $(".error-message").text("请输入6位验证码");
        return;
      }
      invite_code = $("#reg_invitecode").val().trim();
      if (invite_code.length > 0 && invite_code.length !== 6) {
        $(".error-message").text("请输入6位邀请码");
        return;
      }
      $(element).addClass('disable');
      return backend.registerWap({
        identifier: identifier,
        validate_code: validate_code,
        invite_code: invite_code
      }).done(function(data) {
        if (data.ret_code > 0) {
          $(element).removeClass('disable');
          return $(".error-message").text(data.message);
        } else {
          return window.location.href = '/';
        }
      }).fail(function() {
        return $(".error-message").text("注册失败");
      });
    });
  });

}).call(this);
