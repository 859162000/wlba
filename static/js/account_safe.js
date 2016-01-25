(function() {
    require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.validate': 'lib/jquery.validate.min',
      'jquery.modal': 'lib/jquery.modal.min',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.validate': ['jquery'],
      'jquery.modal': ['jquery'],
      "tools": ['jquery.modal']
    }
  });

  require(['jquery', 'lib/modal', 'jquery.validate', 'lib/backend', 'tools'], function($, modal, validate, backend, tool) {
    var csrfSafeMethod, getCookie, sameOrigin,
      getCookie = function (name) {
          var cookie, cookieValue, cookies, i;
          cookieValue = null;
          if (document.cookie && document.cookie !== "") {
              cookies = document.cookie.split(";");
              i = 0;
              while (i < cookies.length) {
                  cookie = $.trim(cookies[i]);
                  if (cookie.substring(0, name.length + 1) === (name + "=")) {
                      cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                      break;
                  }
                  i++;
              }
          }
          return cookieValue;
      };
      csrfSafeMethod = function (method) {
          return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
      };
      sameOrigin = function (url) {
          var host, origin, protocol, sr_origin;
          host = document.location.host;
          protocol = document.location.protocol;
          sr_origin = "//" + host;
          origin = protocol + sr_origin;
          return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
      };



      $.ajaxSetup({
          beforeSend: function (xhr, settings) {
              if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                  xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
              }
          }
      });

      $('.phone_modify_main_wrap_1 .button').click(function(){
          if($('.phone_change_wrap').hasClass('show')){
              $('.phone_change_wrap').removeClass('show').hide();
              $('.phone_modify_main_wrap_1 .button').removeClass('button_is_click');
          }else{
              $('.phone_change_wrap').addClass('show').show();
              $('.phone_modify_main_wrap_1 .button').addClass('button_is_click');
          }
      })


      /*密码管理*/

      $('#setPWDA').click(function() {
          if ($('#id-is-valid').val() === 'false') {
            $('#id-validate').modal();
          } else {
            return window.location.href = '/accounts/back/';
          }
        });
        $('#passwordChangeButton').click(function(e) {
          var params;
          e.preventDefault();
          if ($('#passwordChangeForm').valid()) {
            params = {
              old_password: $('#old-password').val(),
              new_password1: $('#new-password1').val(),
              new_password2: $('#new-password2').val()
            };
            return backend.changePassword(params).done(function() {
              $('#passwordChangeForm').find('input').val('');
              return tool.modalAlert({
                btnText: "确认",
                title: '温馨提示',
                msg: '密码修改成功，请重新登录',
                callback_ok: function() {
                  return window.location.href = '/accounts/logout/?next=/accounts/login/';
                }
              });
            }).fail(function() {
              console.log('Failed to update password, do it again');
              return tool.modalAlert({
                btnText: "确认",
                title: '温馨提示',
                msg: '密码修改失败 请重试'
              });
            });
          }
        });
        $('#passwordChangeForm').validate({
          rules: {
            'old-password': {
              required: true
            },
            'new-password1': {
              required: true,
              minlength: 6
            },
            'new-password2': {
              required: true,
              equalTo: "#new-password1"
            }
          },
          messages: {
            'old-password': {
              required: '不能为空'
            },
            'new-password1': {
              required: '不能为空',
              minlength: $.format("密码需要最少{0}位")
            },
            'new-password2': {
              required: '不能为空',
              equalTo: '两次密码输入不一致'
            }
          }
        });

        /*判断是否设置了交易密码 */
        $.ajax({
          url: "/api/profile/",
          type: "GET",
          data: {}
        }).success(function(data) {
          $('#id-is-valid').val(data.id_is_valid);
          if (data.trade_pwd_is_set) {
            //return $('.old').show();
            $('.old').show();
            $('.phone_modify_main_wrap_2 .pwd-div2 .ico').addClass('is_set_ico').next().text('已设置');
          } else {
            //return $('.new').show();
            $('.new').show();
            $('.phone_modify_main_wrap_2 .pwd-div2 .ico').addClass('no_set_ico').next().text('未设置');
          }
        });
        $.ajax({
          url: "/api/pay/the_one_card/",
          type: "GET",
          data: {}
        }).fail(function() {
          return $('#bankIsNoBind').val('false');
        }).done(function(xhr) {
          return $('#bankIsNoBind').val('true');
        });

    /*找回交易密码 */


      /*实名认证*/
      $.validator.addMethod('idNumber', function(value, element) {
          var reg;
          reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
          return reg.test(value);
        }, '请输入有效身份证');
        $('#validate_id_form').validate({
          rules: {
            name: {
              required: true
            },
            id_number: {
              required: true,
              idNumber: true
            }
          },
          messages: {
            name: {
              required: '请输入姓名'
            },
            id_number: {
              required: '请输入身份证',
              idNumber: '请输入有效身份证'
            }
          },
          errorPlacement: function(error, element) {
            return error.appendTo($(element).closest('.form-row').find('.form-row-error'));
          },
          submitHandler: function(form) {
            var id_number, name;
            name = $('#id_name').val();
            id_number = $('#id_id_number').val();
            if ($("#validate_id_button").hasClass("disabled")) {
              return;
            }
            $("#validate_id_button").addClass('disabled');
            return $.ajax({
              url: '/api/id_validate/',
              data: {
                name: name,
                id_number: id_number
              },
              type: 'post'
            }).done(function() {
              return tool.modalAlert({
                title: '温馨提示',
                msg: '实名认证成功',
                callback_ok: function() {
                  return location.reload();
                }
              });
            }).fail(function(xhr) {
              var result;
              result = JSON.parse(xhr.responseText);
              if (result.error_number === 8) {
                tool.modalAlert({
                  title: '温馨提示',
                  msg: result.message
                });
                return;
              } else if (result.error_number === 9) {
                $("#validate_id_button").removeClass("disabled");
                tool.modalAlert({
                  title: '温馨提示',
                  msg: result.message
                });
              }
              $("#validate_id_button").removeClass("disabled");
              tool.modalAlert({
                title: '温馨提示',
                msg: result.message
              });
              return $('.captcha-refresh', '#validate_id_form').trigger('click');
            });
          }
        });
        return (function() {
          var url;
          url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
          $.getJSON(url, {}, function(json) {
            $('input[name="captcha_0"]').val(json.key);
            return $('img.captcha').attr('src', json.image_url);
          });
        })();
      /*实名认证结束*/






    })

}).call(this);