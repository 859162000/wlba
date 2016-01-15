// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
  });

  require(['jquery', 'lib/modal', 'lib/backend', 'tools', 'lib/calculator'], function($, modal, backend, tool) {
    /*判断是否设置了交易密码 */
    $.ajax({
      url: "/api/profile/",
      type: "GET",
      data: {}
    }).success(function(data) {
      if (data.trade_pwd_is_set) {
        $('#backOne,.zhma').show()
        $('.confirmBtn').attr('tag','1')
        $('#name').text(data.name)
      } else {
        $('#backTwo,.szma').show()
        $('.confirmBtn').attr('tag','2')
      }
    });
    /*获取绑卡状态 */
    $.ajax({
      url: "/api/pay/the_one_card/",
      type: "GET",
      data: {}
    }).fail(function() {
      $('#bankIsNoBind').val('false');
    }).done(function(xhr) {
      var str = xhr.bank.name + '&nbsp;&nbsp;' + xhr.no.substring(0, 3) + '**** ****' + xhr.no.substr(xhr.no.length - 4);
      $('.bindingCard').show().html(str).attr('gate_id', xhr.bank.gate_id);
      $('#bindingEdInfo').html(str).attr('data-no', xhr.no);
    });
    /*设置密码提交表单 */
    $('#nextBtn').click(function() {
      var id, parent, phone, reg, sfzError, yhkh;
      parent = $(this).parent().parent();
      phone = $(this).attr('data-phone');
      id = $.trim(parent.find('.sfz').val());
      yhkh = $('#bindingEdInfo').attr('data-no');
      reg = new RegExp(/^(\d{15}$|^\d{18}$|^\d{17}(\d|X|x))$|[a-zA-Z][a-zA-Z0-9]{1,}$/);
      $('.errorS').html('').hide();
      sfzError = parent.find('#sfzError');
      if (id === '') {
        sfzError.show().addClass('errorS').html('<i></i>请输入身份证号码');
        return;
      } else {
        if (!reg.test(id)) {
          sfzError.show().addClass('errorS').html('<i></i>身份证信息有误');
          return;
        } else {
          sfzError.show().removeClass('errorS').html('<i></i>');
        }
      }
      return $.ajax({
        url: "/api/trade_pwd/",
        type: "POST",
        data: {
          action_type: 3,
          card_id: yhkh,
          citizen_id: id,
          requirement_check: 1
        }
      }).success(function(data) {
        if (data.ret_code === 5) {
            $('#backTwo,.twoStep').show()
            $('#backOne').hide()
        } else {
          return sfzError.show().addClass('errorS').html('<i></i>' + data.message);
        }
      });
    });

    /*确认密码 */
    $('.confirmBtn').click(function() {
      var card_id, citizen_id, dataStr, erro1, erro2, par, pwd1, pwd2, re, tag;
      par = $(this).parent().parent();
      pwd1 = $.trim(par.find('#pwd1').val());
      pwd2 = $.trim(par.find('#pwd2').val());
      erro1 = par.find('#sfzError');
      erro2 = par.find('#yzmError');
      card_id = $.trim($('#bindingEdInfo').attr('data-no'));
      citizen_id = $.trim($('#citizen_id').val());
      tag = $(this).attr('tag');
      re = /^\d{6}$/;
      $('.errorS').html('').hide();
      if (pwd1 === '') {
        erro1.show().addClass('errorS').html('<i></i>请输入密码');
        return;
      } else {
        if (!re.test(pwd1)) {
          erro1.show().addClass('errorS').html('<i></i>格式不正确');
          return;
        } else {
          erro1.show().removeClass('errorS').html('<i></i>');
        }
      }
      if (pwd2 === '') {
        erro2.show().addClass('errorS').html('<i></i>请输入密码');
        return;
      } else {
        if (!re.test(pwd2)) {
          erro2.show().addClass('errorS').html('<i></i>格式不正确');
          return;
        } else {
          erro2.show().removeClass('errorS').html('<i></i>');
        }
      }
      if (pwd1 !== pwd2) {
        erro2.show().addClass('errorS').html('<i></i>交易密码不一致');
        return;
      } else {
        erro2.show().removeClass('errorS').html('<i></i>');
      }
      if (tag === '1') {
        dataStr = 'action_type=3&new_trade_pwd=' + pwd1 + '&card_id=' + card_id + '&citizen_id=' + citizen_id + '&requirement_check=0';
      } else {
        dataStr = 'action_type=1&new_trade_pwd=' + pwd1 + '&requirement_check=0';
      }
      return $.ajax({
        url: "/api/trade_pwd/",
        type: "POST",
        data: dataStr
      }).success(function(xhr) {
        return tool.modalAlert({
          title: '温馨提示',
          msg: xhr.message,
          callback_ok:function(){
              window.location.href='/accounts/setting/';
          }
        });
      });
    });
  });

}).call(this);

//# sourceMappingURL=withdraw.js.map