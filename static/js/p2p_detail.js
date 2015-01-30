// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      tools: 'lib/modal.tools',
      "jquery.validate": 'lib/jquery.validate.min',
      'jquery.modal': 'lib/jquery.modal.min'
    },
    shims: {
      "jquery.validate": ['jquery']
    }
  });

  require(['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown', 'tools', 'lib/modal', "jquery.validate"], function($, _, backend, calculator, countdown, tool, modal) {
    var buildTable, opt, page;
    $.validator.addMethod('dividableBy100', function(value, element) {
      return value % 100 === 0 && !/\./ig.test(value);
    }, '请输入100的整数倍');
    $.validator.addMethod('integer', function(value, element) {
      var notInteger;
      notInteger = /\.\d*[^0]+\d*$/ig.test(value);
      return !($.isNumeric(value) && notInteger);
    }, '请输入整数');
    $.validator.addMethod('positiveNumber', function(value, element) {
      return Number(value) > 0;
    }, '请输入有效金额');
    if ($('#id_amount').attr('p2p-type') === '票据') {
      opt = {
        required: true,
        number: true,
        positiveNumber: true,
        integer: true
      };
    } else {
      opt = {
        required: true,
        number: true,
        positiveNumber: true,
        dividableBy100: true
      };
    }
    $('#purchase-form').validate({
      rules: {
        amount: opt
      },
      messages: {
        amount: {
          required: '请输入投资金额',
          number: '请输入有效金额'
        }
      },
      errorPlacement: function(error, element) {
        return error.appendTo($(element).closest('.form-row__middle').find('.form-row-error'));
      },
      submitHandler: function(form) {
        var tip;
        if ($('.invest').hasClass('notlogin')) {
          $('.login-modal').trigger('click');
          return;
        }
        tip = '您的投资金额为:' + $('input[name=amount]').val() + '元';
        return tool.modalConfirm({
          title: '温馨提示',
          msg: tip,
          callback_ok: function() {
            var amount, product;
            product = $('input[name=product]').val();
            amount = $('input[name=amount]').val();
            return backend.purchaseP2P({
              product: product,
              amount: amount
            }).done(function(data) {
              return tool.modalAlert({
                title: '温馨提示',
                msg: '份额认购成功',
                callback_ok: function() {
                  return window.location.href = "/accounts/home";
                }
              });
            }).fail(function(xhr) {
              var error_message, message, result;
              result = JSON.parse(xhr.responseText);
              if (result.error_number === 1) {
                $('.login-modal').trigger('click');
                return;
              } else if (result.error_number === 2) {
                $('#id-validate').modal();
                return;
              } else if (result.error_number === 4 && result.message === "余额不足") {
                tool.modalAlert({
                  btnText: "去充值",
                  title: '温馨提示',
                  msg: result.message,
                  callback_ok: function() {
                    return window.location.href = '/pay/banks/';
                  }
                });
                return;
              }
              message = result.message;
              error_message = '';
              if ($.type(message) === 'object') {
                error_message = _.chain(message).pairs().map(function(e) {
                  return e[1];
                }).flatten().value();
              } else {
                error_message = message;
              }
              return tool.modalAlert({
                title: '温馨提示',
                msg: error_message
              });
            });
          }
        });
      }
    });
    $("#get-validate-code-buy").click(function() {
      var count, element, intervalId, phoneNumber, timerFunction;
      element = this;
      if ($(element).hasClass('disabled')) {
        return;
      }
      phoneNumber = $(element).attr("data-phone");
      if (!phoneNumber) {
        return;
      }
      $.ajax({
        url: "/api/phone_validation_code/" + phoneNumber + "/",
        type: "POST"
      });
      intervalId;
      count = 60;
      timerFunction = function() {
        if (count >= 1) {
          count--;
          $(element).text('重新获取(' + count + ')');
          if (!$(element).hasClass('disabled')) {
            return $(element).addClass('disabled');
          }
        } else {
          clearInterval(intervalId);
          $(element).text('重新获取');
          return $(element).removeClass('disabled');
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    });
    $('#purchase-form .submit-button').click(function(e) {
      e.preventDefault();
      return $('#purchase-form').submit();
    });
    buildTable = function(list) {
      var html, i, len;
      html = [];
      i = 0;
      len = list.length;
      while (i < len) {
        console.log(list[i].create_time);
        html.push(["<tr>", "<td><p>", list[i].create_time, "</p></td>", "<td><em>", list[i].user, "</em></td>", "<td><span class='money-highlight'>", list[i].amount, "</span><span>元</span></td>", "</tr>"].join(""));
        i++;
      }
      return html.join("");
    };
    page = 2;
    $('.get-more').click(function(e) {
      var id;
      e.preventDefault();
      id = $(this).attr('data-product');
      return $.post('/api/p2p/investrecord', {
        p2p: id,
        page: page
      }).done(function(data) {
        var invest_result;
        try {
          invest_result = $.parseJSON(data);
          if (invest_result && invest_result.length > 0) {
            if (invest_result.length > 0) {
              $('.invest-history-table tbody').append(buildTable(invest_result));
              $('.get-more').show();
              page++;
            } else {
              $('.get-more').hide();
            }
            console.log(invest_result);
          }
        } catch (_error) {
          e = _error;
          $('.get-more').hide();
        }
      });
    });
    return $(".xunlei-binding-modal").click(function() {
      return $('#xunlei-binding-modal').modal();
    });
  });

}).call(this);

//# sourceMappingURL=p2p_detail.js.map
