// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.validate': 'lib/jquery.validate.min'
    },
    shims: {
      'jquery.validate': ['jquery']
    }
  });

  require(['jquery', 'jquery.validate', 'lib/backend'], function($, validate, backend) {
    var checkEmail, checkMobile;
    checkEmail = function(identifier) {
      var re;
      re = void 0;
      re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(identifier);
    };
    checkMobile = function(identifier) {
      var re;
      re = void 0;
      re = /^1\d{10}$/;
      return re.test(identifier);
    };
    $("#id_identifier").keyup(function(e) {
      var isEmail, isMobile, value;
      isEmail = void 0;
      isMobile = void 0;
      value = void 0;
      value = $(this).val();
      isMobile = checkMobile(value);
      isEmail = checkEmail(value);
      if (isMobile) {
        $("#id_type").val("phone");
        return $("#validate-code-container").show();
      } else if (isEmail) {
        $("#id_type").val("email");
        return $("#validate-code-container").hide();
      } else {
        $("#id_type").val("email");
        return $("#validate-code-container").hide();
      }
    });
    $("#id_identifier").keyup();
    $("#button-get-validate-code").click(function(e) {
      var element, phoneNumber;
      e.preventDefault();
      element = this;
      e.preventDefault();
      phoneNumber = $("#id_identifier").val().trim();
      if (checkMobile(phoneNumber)) {
        if (typeof console !== "undefined" && console !== null) {
          console.log("Phone number checked, now send the valdiation code");
        }
        return $.ajax({
          url: "/api/phone_validation_code/register/" + phoneNumber + "/",
          type: "POST"
        }).done(function() {
          intervalId;
          var count, intervalId, timerFunction;
          count = 60;
          $(element).attr('disabled', 'disabled');
          timerFunction = function() {
            if (count >= 1) {
              count--;
              return $(element).text('重新获取(' + count + ')');
            } else {
              clearInterval(intervalId);
              $(element).text('重新获取');
              return $(element).removeAttr('disabled');
            }
          };
          timerFunction();
          return intervalId = setInterval(timerFunction, 1000);
        });
      }
    });
    $.validator.addMethod("emailOrPhone", function(value, element) {
      return checkEmail(value) || checkMobile(value);
    });
    return $('#register-form').validate({
      rules: {
        identifier: {
          required: true,
          emailOrPhone: true
        },
        password: {
          required: true,
          minlength: 6
        },
        'validation_code': {
          required: true,
          depends: function(e) {
            return checkMobile($('#id_identifier').val());
          }
        }
      },
      messages: {
        identifier: {
          required: '不能为空',
          emailOrPhone: '请输入邮箱或者手机号'
        },
        password: {
          required: '不能为空',
          minlength: $.format("密码需要最少{0}位")
        },
        'validation_code': {
          required: '不能为空'
        }
      }
    });
  });

}).call(this);

//# sourceMappingURL=register.map
