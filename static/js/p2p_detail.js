// Generated by CoffeeScript 1.7.1
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
    var buildTable, ddData, opt, page;
    $('.payment2').hide();
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
    }, '');
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
          var available_time, availables, datetime, desc, obj, _i, _len;
          availables = data.packages.available;
          ddData.push({
            text: '不使用红包',
            value: '',
            selected: true,
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
              selected: false,
              amount: obj.amount,
              invest_amount: obj.invest_amount,
              description: desc + ', ' + available_time + '过期'
            });
          }
          $('.red-pack').ddslick({
            data: ddData,
            width: 194,
            imagePosition: "left",
            selectText: "请选择红包",
            onSelected: function(data) {
              var lable, pay_amount;
              obj = data.selectedData;
              if (obj.value !== '') {
                if (obj.amount !== 0) {
                  pay_amount = $('#id_amount').val();
                  $.ajax({
                    url: '/api/redpacket/deduct/',
                    data: {
                      amount: pay_amount,
                      rpa: obj.amount
                    },
                    type: 'post'
                  }).done(function(data) {
                    $('.payment2').show();
                    $('.payment').hide();
                    $('.payment2').html(['红包使用<i>', data.deduct, '</i>元，', '实际支付<i>', pay_amount - data.deduct, '</i>元'].join('')).css({
                      color: '#999'
                    });
                    return $('.payment2 i').css({
                      color: '#1A2CDB'
                    });
                  });
                }
                if ($('#id_amount').val() - obj.invest_amount < 0) {
                  $('.payment2').html('投资金额未达到红包使用门槛').css({
                    color: 'red'
                  });
                  lable = $('label[for="id_amount"]');
                  if ($.trim(lable.text()) === '') {
                    $('label[for="id_amount"]').hide();
                  }
                }
              } else if ($('#id_amount').val()) {
                pay_amount = $('#id_amount').val();
                $('.payment').show();
                $('.payment2').hide();
                $('.payment').html(['实际支付<i>', pay_amount, '</i>元，'].join('')).css({
                  color: '#999'
                });
                $('.payment i').css({
                  color: '#1A2CDB'
                });
              }
            }
          });
          return $('#id_amount').keyup(function(e) {
            var amount, lable, max_pay, pay_amount, selectedData, _j, _len1;
            max_pay = $('#id_amount').attr('data-max');
            if ($('#id_amount').val() !== max_pay) {
              for (_j = 0, _len1 = ddData.length; _j < _len1; _j++) {
                obj = ddData[_j];
                if (obj.value === $('.dd-selected-value').val() * 1) {
                  selectedData = obj;
                  break;
                }
              }
              amount = $('#id_amount').val();
              if (selectedData) {
                if (amount - selectedData.invest_amount >= 0) {
                  pay_amount = $('#id_amount').val();
                  $.ajax({
                    url: '/api/redpacket/deduct/',
                    data: {
                      amount: pay_amount,
                      rpa: obj.amount
                    },
                    type: 'post'
                  }).done(function(data) {
                    $('.payment2').show();
                    $('.payment').hide();
                    $('.payment2').html(['红包使用<i>', data.deduct, '</i>元，', '实际支付<i>', pay_amount - data.deduct, '</i>元'].join('')).css({
                      color: '#999'
                    });
                    return $('.payment2 i').css({
                      color: '#1A2CDB'
                    });
                  });
                } else {
                  $('.payment2').html('投资金额未达到红包使用门槛').css({
                    color: 'red'
                  });
                  lable = $('label[for="id_amount"]');
                  if ($.trim(lable.text()) === '') {
                    $('label[for="id_amount"]').hide();
                  }
                }
              } else if ($.isNumeric(amount) && amount > 0) {
                pay_amount = $('#id_amount').val();
                $.ajax({
                  url: '/api/redpacket/deduct/',
                  data: {
                    amount: pay_amount,
                    rpa: 0
                  },
                  type: 'post'
                }).done(function(data) {
                  $('.payment2').hide();
                  $('.payment').html(['实际支付<i>', pay_amount, '</i>元，'].join('')).css({
                    color: '#999'
                  });
                  return $('.payment i').css({
                    color: '#1A2CDB'
                  });
                });
              } else {
                $('.payment').show();
                $('.payment').html(['实际支付 0 元'].join('')).css({
                  color: '#999'
                });
              }
            } else {
              XMLHttpRequest.readyState = 0;
            }
            return $('#id_amount').blur(function(e) {
              lable = $('label[for="id_amount"]');
              if ($.trim(lable.text()) === '') {
                return $('label[for="id_amount"]').hide();
              }
            });
          });
        });
      });
    }
  });

}).call(this);
