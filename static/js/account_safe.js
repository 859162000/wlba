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

      $('.phone_modify_main_wrap_1 .phone_change_button').click(function() {
        if ($('.phone_change_wrap').length) {
          if ($('.phone_change_wrap').hasClass('show')) {
            $('.phone_change_wrap').removeClass('show').hide();
            $('.phone_modify_main_wrap_1 .phone_change_button').removeClass('button_is_click');
          } else {
            $('.phone_change_wrap').addClass('show').show();
            $('.phone_modify_main_wrap_1 .phone_change_button').addClass('button_is_click');
          }
        }else{
          //3秒后跳转到实名认证地址
          $('.phone_modify_popup').show();
          var time_count = 2;
          var timerFunction = function () {
              if (time_count > 0) {
                  time_count--;
                  return
              } else {
                  clearInterval(timerFunction);
                  window.location.href = '/accounts/id_verify/';
              }
          };
          setInterval(timerFunction, 1000);
        }
      })

      /**/
      $('.people_wrap').click(function(){
          if(true){
              window.location.href = '/accounts/manual_modify/vali_acc_info/';
          }else{
              $('.tieOnCard_popup').show();
          }
      })

      $('.tieOnCard_popup .close_ico').click(function(){
          $('.tieOnCard_popup').hide();
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
            $('.phone_modify_main_wrap_2 .pwd-div2 .ico').addClass('is_set_ico').next().text('已设置').addClass('is_set_text');
          } else {
            //return $('.new').show();
            $('.new').show();
            $('.phone_modify_main_wrap_2 .pwd-div2 .ico').addClass('no_set_ico').next().text('未设置').addClass('no_set_text');
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

    })

}).call(this);