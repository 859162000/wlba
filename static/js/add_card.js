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
        $('.bankName').text(par.find('.select_bank option:selected').text() + '（储蓄卡）');
        $('.bankId').text(card.val().replace(/\s/g, '').replace(/(\d{4})(?=\d)/g, "$1 "));
        $('#confirmInfo').show();
        return $('#chooseBank,.bankTitle span').hide();
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
        re = /^\d{10,20}$/;
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
      btns = $('#bindingBtn');
      return _checkPerInfo(btns);
    });

    /*验证个人信息 */
    _checkPerInfo = function(btns) {
      var bankPhone, code;
      bankPhone = btns.parent().parent().find('.bankPhone');
      code = btns.parent().parent().find('.code');
      if (!_checkMobile(bankPhone)) {

      } else {
        if (code.val() === '') {
          code.parent().find('span').html('<i class="cha"></i>请填写验证码');
        } else {
          code.parent().find('span').html('<i class="dui"></i>');
          return $.ajax({
            url: '',
            data: {},
            type: 'post'
          }).done(function() {
            return console.log('11111');
          }).fail(function(xhr) {
            return console.log('222222');
          });
        }
      }
    };
    $('#withdrawBindingBtn').click(function() {
      var bank, btn, card, par;
      par = $(this).parent().parent();
      bank = par.find('.select_bank');
      card = par.find('.cardId');
      btn = $('#withdrawBindingBtn');
      _checkBankCard(bank, card);
      return _checkPerInfo(btn);
    });
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
      phoneNumber = $(element).attr("data-phone");
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
        var result;
        clearInterval(intervalId);
        $(element).text('重新获取');
        $(element).removeAttr('disabled');
        $(element).addClass('go-get-code');
        result = JSON.parse(xhr.responseText);
        return tool.modalAlert({
          title: '温馨提示',
          msg: result.message
        });
      }).success(function() {
        element.attr('disabled', 'disabled');
        return element.removeClass('go-get-code');
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
          return $(element).removeAttr('disabled');
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    });

    /*绑定银行卡 */
    $('.binding-card').click(function() {
      var card, par, str;
      $('#bindingOldCard').modal();
      $('#bindingOldCard').find('.ok-btn').attr({
        'data-card': $(this).attr('data-card')
      });
      $('#bindingOldCard').find('.close-modal').hide();
      $('.modal').css({
        'width': '560px'
      });
      par = $(this).parent();
      card = par.find('.bank-card--info-value').text();
      str = par.find('.bankname').attr('title') + '尾号' + card.substr(card.length - 4);
      return $('.bankInfo').html(str);
    });

    /*确认绑定 */
    $('.ok-btn').click(function() {
      return $.ajax({
        url: '/api/pay/the_one_card/',
        data: {
          card_id: $(this).attr('data-card')
        },
        type: 'put'
      }).done(function() {
        return console.log('111111');
      }).fail(function(xhr) {
        return console.log('222222');
      });
    });

    /*取消绑定 */
    $('.no-btn').click(function() {
      return $.modal.close();
    });
    $('.change-bank').click(function() {
      $('#confirmInfo').hide();
      return $('#chooseBank,.bankTitle span').show();
    });
    $('.captcha-refresh').click(function() {
      var $form;
      $form = $(this).parents('form');
      url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
      return $.getJSON(url, {}, function(json) {
        $form.find('input[name="captcha_0"]').val(json.key);
        return $form.find('img.captcha').attr('src', json.image_url);
      });
    });
    $('#add-card-button').click(function(e) {
      if ($('#id-is-valid').val() === 'False') {
        $('#id-validate').modal();
        return;
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
