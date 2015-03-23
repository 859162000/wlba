// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      tools: 'lib/modal.tools',
      "jquery.validate": 'lib/jquery.validate.min',
      'jquery.modal': 'lib/jquery.modal.min',
      ddslick: 'lib/jquery.ddslick.min'
    },
    shims: {
      "jquery.validate": ['jquery'],
      "ddslick": ['jquery']
    }
  });

  require(['jquery', 'underscore', 'lib/backend', 'lib/calculator', 'lib/countdown', 'tools', 'lib/modal', "jquery.validate", 'ddslick'], function($, _, backend, calculator, countdown, tool, modal) {
    var buildTable, ddData, getRedAmount, getRedPack, hideEmptyLabel, isFirst, opt, page, showPayInfo, showPayTip, validator;
    isFirst = true;
    showPayInfo = function(actual_payment, red_pack_payment) {
      return ['红包使用<i class="blue">', red_pack_payment, '</i>元，实际支付<i class="blue">', actual_payment, '</i>元'].join('');
    };
    getRedAmount = function(method, red_pack_amount, event_id) {
      var amount, final_redpack, flag;
      amount = $('#id_amount').val();
      if (event_id === '7') {
        flag = amount * 0.005;
        if (flag <= 30) {
          final_redpack = flag;
        } else {
          final_redpack = 30;
        }
        return {
          red_pack: final_redpack,
          actual_amount: amount - final_redpack
        };
      }
      if (method === '*') {
        final_redpack = amount * red_pack_amount;
      } else {
        final_redpack = red_pack_amount;
      }
      return {
        red_pack: final_redpack,
        actual_amount: amount - final_redpack
      };
    };
    hideEmptyLabel = function(e) {
      return setTimeout((function() {
        var lable;
        lable = $('label[for="id_amount"]');
        if ($.trim(lable.text()) === '') {
          return $('label[for="id_amount"]').hide();
        }
      }), 10);
    };
    getRedPack = function() {
      var obj, selectedData, _i, _len;
      for (_i = 0, _len = ddData.length; _i < _len; _i++) {
        obj = ddData[_i];
        if (obj.value === $('.dd-selected-value').val() * 1) {
          selectedData = obj;
          break;
        }
      }
      return selectedData;
    };
    showPayTip = function(method, amount) {
      var html, redPack, redPackInfo;
      redPack = getRedPack();
      redPackInfo = getRedAmount(redPack.method, redPack.amount, redPack.event_id);
      html = showPayInfo(redPackInfo.actual_amount, redPackInfo.red_pack);
      return $('.payment').html(html).show();
    };
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
    $.validator.addMethod('threshold', function(value, element) {
      var obj, selectedData, _i, _len;
      for (_i = 0, _len = ddData.length; _i < _len; _i++) {
        obj = ddData[_i];
        if (obj.value === $('.dd-selected-value').val() * 1) {
          selectedData = obj;
          break;
        }
      }
      if (selectedData) {
        return $('#id_amount').val() - selectedData.invest_amount >= 0;
      } else {
        return true;
      }
    }, '投资金额未达到红包使用门槛');
    if ($('#id_amount').attr('p2p-type') === '票据') {
      opt = {
        required: true,
        number: true,
        positiveNumber: true,
        integer: true,
        threshold: true
      };
    } else {
      opt = {
        required: true,
        number: true,
        positiveNumber: true,
        dividableBy100: true,
        threshold: true
      };
    }
    validator = $('#purchase-form').validate({
      rules: {
        amount: opt
      },
      messages: {
        amount: {
          required: '请输入投资金额',
          number: '请输入数字'
        }
      },
      errorPlacement: function(error, element) {
        $('.payment').hide();
        return error.appendTo($(element).closest('.form-row__middle').find('.form-row-error'));
      },
      success: function() {
        if ($('.dd-selected-value').val() !== '') {
          return $('#purchase-form').trigger('redpack');
        }
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
            var amount, product, redpack_id;
            product = $('input[name=product]').val();
            amount = $('input[name=amount]').val();
            redpack_id = $('.dd-selected-value').val();
            return backend.purchaseP2P({
              product: product,
              amount: amount,
              redpack: redpack_id
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
    $('#purchase-form').on('redpack', function() {
      return showPayTip();
    });
    $('#id_amount').blur(hideEmptyLabel);
    $('#id_amount').keyup(hideEmptyLabel);
    buildTable = function(list) {
      var html, i, len;
      html = [];
      i = 0;
      len = list.length;
      while (i < len) {
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
          }
        } catch (_error) {
          e = _error;
          $('.get-more').hide();
        }
      });
    });
    $(".xunlei-binding-modal").click(function() {
      return $('#xunlei-binding-modal').modal();
    });
    ddData = [];
    if ($('.red-pack').size() > 0) {
      return $(document).ready(function() {
        $.post('/api/redpacket/', {
          status: 'available'
        }).done(function(data) {
          var available_time, availables, data2, datetime, desc, obj, _i, _len;
          data2 = data;
          availables = data.packages.available;
          ddData.push({
            text: '不使用红包',
            value: '',
            selected: true,
            method: '',
            amount: 0,
            invest_amount: 0,
            description: '不使用红包'
          });
          for (_i = 0, _len = availables.length; _i < _len; _i++) {
            obj = availables[_i];
            desc = (obj.invest_amount && obj.invest_amount > 0 ? "投资" + obj.invest_amount + "元可用" : "无投资门槛");
            datetime = new Date();
            datetime.setTime(obj.unavailable_at * 1000);
            available_time = [datetime.getFullYear(), datetime.getMonth() + 1, datetime.getDate()].join('-');
            ddData.push({
              text: obj.name,
              value: obj.id,
              method: obj.method,
              selected: false,
              amount: obj.amount,
              invest_amount: obj.invest_amount,
              description: desc + ', ' + available_time + '过期'
            });
          }
          return $('.red-pack').ddslick({
            data: ddData,
            width: 194,
            imagePosition: "left",
            selectText: "请选择红包",
            onSelected: function(data) {
              if (validator.checkForm() && $('.dd-selected-value').val() !== '') {
                $('#purchase-form').trigger('redpack');
              } else {
                $('.payment').hide();
                if (!isFirst) {
                  $('#purchase-form').valid();
                }
              }
              return isFirst = true;
            }
          });
        });
      });
    }
  });

}).call(this);
