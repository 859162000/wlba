// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'jquery.placeholder': 'lib/jquery.placeholder',
      'jquery.validate': 'lib/jquery.validate.min',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.placeholder': ['jquery'],
      'jquery.validate': ['jquery']
    }
  });

  require(['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder', 'jquery.validate', 'tools'], function($, modal, backend, placeholder, validate, tool) {
    var card_id, url, _checkBankCard, _checkMobile, _checkPerInfo, _delCard, _showModal;
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
    $.getJSON(url, {}, function(json) {
      $('#withdraw-form').find('input[name="captcha_0"]').val(json.key);
      return $('#withdraw-form').find('img.captcha').attr('src', json.image_url);
    });
    $('input, textarea').placeholder();

    /*选择银行卡下拉框 */
    $('.select_bank').focus(function() {
      return $('.select_bank').addClass('selected');
    });
    $('.select_bank').blur(function() {
      if ($(this).val() === '') {
        return $('.select_bank').removeClass('selected');
      }
    });

    /*提交银行卡信息 */
    $('#goPersonalInfo').click(function() {
      var bank, card, par;
      par = $(this).parent().parent();
      bank = par.find('.select_bank');
      card = par.find('.cardId');
      if (_checkBankCard(bank, card)) {
        card.next().html('<i class="dui"></i>');
        if ($('#goPersonalInfo').attr('data-type') === 'special') {
          return $.ajax({
            url: "/api/card/",
            type: "POST",
            data: {
              no: card.val().replace(/\s/g, ''),
              is_default: false,
              bank: par.find('.select_bank option:selected').attr('data-id')
            }
          }).success(function(data) {
            return location.reload();
          }).fail(function(xhr) {
            var result;
            result = JSON.parse(xhr.responseText);
            tool.modalAlert({
              title: '温馨提示',
              msg: result.message
            });
          });
        } else {
          $('.bankName').text(par.find('.select_bank option:selected').text() + '（储蓄卡）');
          $('.bankId').text(card.val().replace(/\s/g, '').replace(/(\d{4})(?=\d)/g, "$1 "));
          $('#confirmInfo').show();
          return $('#chooseBank,.bankTitle span').hide();
        }
      }
    });

    /*验证银行卡信息 */
    _checkBankCard = function(bank, card) {
      var checkIsOrNo, re;
      checkIsOrNo = false;
      if (bank.val() === '') {
        bank.next().html('<i class="cha"></i>请选择银行');
        checkIsOrNo = false;
      } else {
        bank.next().html('<i class="dui"></i>');
        checkIsOrNo = true;
      }
      if (card.val() === '') {
        card.next().html('<i class="cha"></i>请输入卡号');
        checkIsOrNo = false;
      } else {
        re = /^\d{11,20}$/;
        if (!re.test(card.val().replace(/[ ]/g, ""))) {
          card.next().html('<i class="cha"></i>输入的卡号有误');
          checkIsOrNo = false;
        } else {
          card.next().html('<i class="dui"></i>');
          checkIsOrNo = true;
        }
      }
      return checkIsOrNo;
    };

    /*个人信息 */
    $('#bindingBtn').click(function() {
      var btns;
      if (!$(this).hasClass('bunsNo')) {
        btns = $('#bindingBtn');
        return _checkPerInfo(btns);
      }
    });

    /*验证个人信息 */
    _checkPerInfo = function(btns) {
      var bankId, bankPhone, code;
      bankPhone = btns.parent().parent().find('.bankPhone');
      code = btns.parent().parent().find('.code');
      if (!_checkMobile(bankPhone)) {

      } else {
        if (code.val() === '') {
          code.parent().find('span').html('<i class="cha"></i>请填写验证码');
          return;
        }
        if ($('#order_id').val() === '') {
          tool.modalAlert({
            title: '温馨提示',
            msg: '请发送验证码'
          });
          return;
        }
        code.parent().find('span').html('<i class="dui"></i>');
        bankId = $('.bankId').text().replace(/[ ]/g, "");
        $('#bindingBtn').addClass('bunsNo');
        return $.ajax
          url: '/api/pay/cnp/dynnum_new/',
          data: {
            Storable_no: bankId.substr(0, 4) + bankId.substr(bankId.length - 4),
            card_no: bankId,
            vcode: $('.sem-input').val(),
            order_id: $('#order_id').val(),
            token: $('#token').val(),
            phone: $('.bankPhone').val(),
            device_id: ''
          },
          type: 'post'
        }).done(function(xhr) {
          if (xhr.ret_code === 0 || xhr.ret_code === 22000) {
            location.reload();
          } else {
            tool.modalAlert({
              title: '温馨提示',
              msg: xhr.message
            });
            $('#bindingBtn').removeClass('bunsNo');
          }
        }).fail(function(xhr) {
          tool.modalAlert({
            title: '温馨提示',
            msg: xhr.message
          });
          $('#bindingBtn').removeClass('bunsNo');
        });
      }
    };
    $('.bankPhone').blur(function() {
      if (_checkMobile($(this))) {
        return $('.get-code').addClass('go-get-code');
      } else {
        return $('.get-code').removeClass('go-get-code');
      }
    });

    /*验证手机号 */
    _checkMobile = function(bankPhone) {
      var checkIsNo, identifier, re;
      checkIsNo = false;
      re = /^1\d{10}$/;
      identifier = bankPhone.val();
      if (identifier === '') {
        bankPhone.next().html('<i class="cha"></i>请填写手机号');
        checkIsNo = false;
      } else {
        if (!re.test(identifier)) {
          bankPhone.next().html('<i class="cha"></i>格式不正确');
          checkIsNo = false;
        } else {
          bankPhone.next().html('<i class="dui"></i>');
          checkIsNo = true;
        }
      }
      return checkIsNo;
    };

    /*银行卡格式 */
    $(".cardId").keydown(function() {
      var value;
      value = $(this).val().replace(/\s/g, '').replace(/(\d{4})(?=\d)/g, "$1 ");
      return $(this).val(value);
    });

    /*短信验证码 */
    $('.codeBox').delegate('.go-get-code', 'click', function() {
      var count, element, intervalId, phoneNumber, timerFunction;
      element = $('.get-code');
      if ($(element).attr('disabled')) {
        return;
      }
      phoneNumber = $('.bankPhone').val();
      $.ajax({
        url: "/api/pay/deposit_new/",
        type: "POST",
        data: {
          card_no: $('.cardId').val().replace(/[ ]/g, ""),
          phone: phoneNumber,
          amount: 0.01,
          gate_id: $('.select_bank').val(),
          device_id: ''
        }
      }).fail(function(xhr) {
        clearInterval(intervalId);
        $(element).text('重新获取');
        $(element).removeAttr('disabled');
        $(element).addClass('go-get-code');
        return tool.modalAlert({
          title: '温馨提示',
          msg: xhr.message
        });
      }).success(function(xhr) {
        if (xhr.ret_code === 0) {
          element.attr('disabled', 'disabled');
          element.removeClass('go-get-code');
          $('#order_id').val(xhr.order_id);
          return $('#token').val(xhr.token);
        } else {
          clearInterval(intervalId);
          $(element).text('重新获取');
          $(element).removeAttr('disabled');
          $(element).addClass('go-get-code');
          return tool.modalAlert({
            title: '温馨提示',
            msg: xhr.message
          });
        }
      });
      intervalId;
      count = 60;
      $(element).attr('disabled', 'disabled');
      timerFunction = function() {
        if (count >= 1) {
          count--;
          return $(element).text('重新获取(' + count + ')');
        } else {
          clearInterval(intervalId);
          $(element).text('重新获取');
          $(element).removeAttr('disabled');
          return $(element).addClass('go-get-code');
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    });

    /*绑定银行卡 */

    /*确认绑定 */

    /*取消绑定 */
    $('.change-bank').click(function() {
      $('#confirmInfo').hide();
      return $('#chooseBank,.bankTitle span').show();
    });
    $('.captcha-refresh').click(function() {
      var $form;
      $form = $(this).parents('form');
      url = location.protocol + "//" + window.location.hostname + ":" + location.port + "captcha-refresh";
      return $.getJSON(url, {}, function(json) {
        $form.find('input[name="captcha_0"]').val(json.key);
        return $form.find('img.captcha').attr('src', json.image_url);
      });
    });
    $('#add-card-button').click(function(e) {
      if ($('#id-is-valid').attr('data-type') === 'qiye') {
        if ($('#id-is-valid').val() === 'False') {
          $.ajax({
            url: '/qiye/profile/exists/',
            data: {},
            type: 'GET'
          }).done(function(data) {
            if (data.ret_code === 10000) {
              return $.ajax({
                url: '/qiye/profile/get/',
                data: {},
                type: 'GET'
              }).done(function(data) {
                if (data.data.status !== '审核通过') {
                  return $('.verifyHref').attr('href', '/qiye/profile/edit/');
                }
              });
            }
          }).fail(function(data) {
            return $('.verifyHref').attr('href', '/qiye/info/');
          });
          $('#id-validate').modal();
          return;
        }
      } else {
        if ($('#id-is-valid').val() === 'False') {
          $('#id-validate').modal();
          $.ajax({
            url: "/api/profile/",
            type: "GET",
            data: {}
          }).success(function(data) {
            if (data.is_mainland_user === false) {
              $('#goPersonalInfo').attr({
                'data-type': 'special'
              });
              return $('#goPersonalInfo').text('绑定银行卡');
            }
          });
          return;
        }
      }
      e.preventDefault();
      $('.banks-list,.bankManage').hide();
      return $('#chooseBank,.bankTitle').show();
    });
    _showModal = function() {
      return $('#add-card-button').modal();
    };
    $('#add-card').click(function(e) {
      var bank_id, card_no, is_default;
      e.preventDefault();
      card_no = $('#card-no').val();
      if (!backend.checkCardNo(card_no)) {
        tool.modalAlert({
          title: '温馨提示',
          msg: '请输入有效的银行卡号',
          callback_ok: _showModal
        });
        return;
      }
      bank_id = $('#bank-select').val();
      if (!bank_id) {
        tool.modalAlert({
          title: '温馨提示',
          msg: '请选择银行',
          callback_ok: _showModal
        });
        return;
      }
      is_default = $('#default-checkbox').prop('checked');
      return $.ajax({
        url: '/api/card/',
        data: {
          no: card_no,
          bank: bank_id,
          is_default: is_default
        },
        type: 'post'
      }).done(function() {
        return location.reload();
      }).fail(function(xhr) {
        var result;
        $.modal.close();
        result = JSON.parse(xhr.responseText);
        if (result.error_number === 5) {
          tool.modalAlert({
            title: '温馨提示',
            msg: result.message
          });
          return;
        }
        return tool.modalAlert({
          title: '温馨提示',
          msg: '添加银行卡失败'
        });
      });
    });
    card_id = "";
    $('a#del-card').click(function(e) {
      card_id = $(this).attr("card_id");
      return tool.modalConfirm({
        title: '温馨提示',
        msg: '确定删除？',
        callback_ok: _delCard
      });
    });
    return _delCard = function() {
      return $.ajax({
        url: '/api/card/' + card_id + '/',
        data: {
          card_id: card_id
        },
        type: 'delete'
      }).done(function() {
        return location.reload();
      }).fail(function(xhr) {
        var result;
        $.modal.close();
        result = JSON.parse(xhr.responseText);
        if (result.error_number === 5) {
          tool.modalAlert({
            title: '温馨提示',
            msg: result.message
          });
          return;
        }
        return tool.modalAlert({
          title: '温馨提示',
          msg: '删除失败'
        });
      });
    };
  });

}).call(this);

//# sourceMappingURL=add_card.js.map
