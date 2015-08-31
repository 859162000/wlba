// Generated by CoffeeScript 1.9.3
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
    var buildTable, clearToShow, ddData, getActualAmount, getFormatedNumber, getRedAmount, getRedPack, hideEmptyLabel, isFirst, opt, page, showPayIncrease, showPayInfo, showPayTip, validator;
    isFirst = true;
    getFormatedNumber = function(num) {
      return Math.round(num * 100) / 100;
    };
    clearToShow = function(arr) {
      var i;
      i = 0;
      while (arr[i] && arr.length) {
        if ($.trim($(arr[i]).text()) === '') {
          arr.splice(i, 1);
        } else {
          i++;
        }
      }
      return arr;
    };
    getActualAmount = function(investAmount, redpackAmount) {
      if (investAmount <= redpackAmount) {
        return 0;
      } else {
        return getFormatedNumber(investAmount - redpackAmount);
      }
    };
    showPayInfo = function(actual_payment, red_pack_payment) {
      return ['红包使用<i class="blue">', red_pack_payment, '</i>元，实际支付<i class="blue">', actual_payment, '</i>元'].join('');
    };
    showPayIncrease = function(redpack_amount, increase) {
      return ['额外加息<i class="blue">', redpack_amount * 100, '% </i>, 预期额外收益<i class="blue">', increase, '</i>元'].join('');
    };
    getRedAmount = function(method, red_pack_amount, event_id, highest_amount) {
      var $amount, amount, final_redpack, p2p_data;
      $amount = $('#id_amount');
      amount = $amount.val();
      if (method === '*') {
        final_redpack = amount * red_pack_amount;
        if (highest_amount && highest_amount < final_redpack) {
          final_redpack = highest_amount;
        }
      } else if (method === '-') {
        final_redpack = red_pack_amount;
      } else {
        p2p_data = {
          period: $amount.attr('data-period') * 1,
          method: $amount.attr('data-paymethod')
        };
        final_redpack = calculator(amount, red_pack_amount, p2p_data.period, p2p_data.method);
      }
      return {
        red_pack: getFormatedNumber(final_redpack),
        actual_amount: getActualAmount(amount, final_redpack)
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
      var j, len1, obj, selectedData;
      for (j = 0, len1 = ddData.length; j < len1; j++) {
        obj = ddData[j];
        if (obj.value === $('.dd-selected-value').val() * 1) {
          selectedData = obj;
          break;
        }
      }
      return selectedData;
    };
    showPayTip = function(method, amount) {
      var highest_amount, html, redPack, redPackInfo;
      redPack = getRedPack();
      if (!redPack) {
        return;
      }
      highest_amount = 0;
      if (redPack.highest_amount) {
        highest_amount = redPack.highest_amount;
      }
      redPackInfo = getRedAmount(redPack.method, redPack.amount, redPack.event_id, highest_amount);
      if (redPack.method === '~') {
        html = showPayIncrease(redPack.amount, redPackInfo.red_pack);
      } else {
        html = showPayInfo(redPackInfo.actual_amount, redPackInfo.red_pack);
      }
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
      var j, len1, obj, selectedData;
      for (j = 0, len1 = ddData.length; j < len1; j++) {
        obj = ddData[j];
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
        return error.appendTo($(element).closest('.form-row__middle').find('.form-row-error'));
      },
      showErrors: function(errorMap, errorList) {
        var elements, error, i;
        i = 0;
        while (this.errorList[i]) {
          error = this.errorList[i];
          if (this.settings.highlight) {
            this.settings.highlight.call(this, error.element, this.settings.errorClass, this.settings.validClass);
          }
          this.showLabel(error.element, error.message);
          i++;
        }
        if (this.errorList.length) {
          this.toShow = this.toShow.add(this.containers);
        }
        if (this.settings.success) {
          i = 0;
          while (this.successList[i]) {
            this.showLabel(this.successList[i]);
            i++;
          }
        }
        if (this.settings.unhighlight) {
          i = 0;
          elements = this.validElements();
          while (elements[i]) {
            this.settings.unhighlight.call(this, elements[i], this.settings.errorClass, this.settings.validClass);
            i++;
          }
        }
        this.toHide = this.toHide.not(this.toShow);
        this.hideErrors();
        this.toShow = clearToShow(this.toShow);
        return this.addWrapper(this.toShow).show();
      },
      success: function() {
        if ($('.dd-selected-value').val() !== '') {
          return $('#purchase-form').trigger('redpack');
        }
      },
      highlight: function(element, errorClass, validClass) {
        if ($(element).attr('id') === 'id_amount') {
          return $('.payment').hide();
        }
      },
      unhighlight: function(element, errorClass, validClass) {
        if ($(element).attr('id') === 'id_amount') {
          return hideEmptyLabel();
        }
      },
      invalidHandler: function(event, validator) {
        return $('.payment').hide();
      },
      onfocusout: false,
      debug: true,
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
                  if (data.category === '酒仙众筹标') {
                    return window.location.href = "/accounts/home/jiuxian/";
                  } else {
                    return window.location.href = "/accounts/home";
                  }
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
              if (math.ceil(invest_result.length / 30) < page) {
                return $('.get-more').hide();
              }
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
          status: 'available',
          product_id: $('input[name=product]').val()
        }).done(function(data) {
          var amount, available_time, availables, data2, datetime, desc, highest_amount, j, len1, obj, text;
          data2 = data;
          availables = data.packages.available;
          ddData.push({
            text: '不使用优惠券',
            value: '',
            selected: true,
            method: '',
            amount: 0,
            invest_amount: 0,
            highest_amount: 0,
            event_id: 0,
            description: '不使用优惠券'
          });
          for (j = 0, len1 = availables.length; j < len1; j++) {
            obj = availables[j];
            datetime = new Date();
            datetime.setTime(obj.unavailable_at * 1000);
            available_time = [datetime.getFullYear(), datetime.getMonth() + 1, datetime.getDate()].join('-');
            highest_amount = 0;
            if (obj.method === '*') {
              amount = obj.highest_amount;
              desc = ['抵', obj.amount * 100, '%投资额'].join('');
            } else if (obj.method === '-') {
              amount = obj.amount;
              desc = (obj.invest_amount && obj.invest_amount > 0 ? [obj.invest_amount, "元起用"].join('') : "无投资门槛");
            } else {
              amount = '';
              desc = (obj.invest_amount && obj.invest_amount > 0 ? [obj.invest_amount, "元起用"].join('') : "无投资门槛");
            }
            if (obj.highest_amount) {
              highest_amount = obj.highest_amount;
            }
            if (obj.method === '~') {
              text = [obj.name, ' 加息', obj.amount * 100, '%'].join('');
            } else {
              text = [obj.name, ' ', amount, '元'].join('');
            }
            ddData.push({
              text: text,
              value: obj.id,
              method: obj.method,
              selected: false,
              amount: obj.amount,
              invest_amount: obj.invest_amount,
              event_id: obj.event_id,
              highest_amount: highest_amount,
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
              }
              if (!isFirst) {
                $('#purchase-form').valid();
                hideEmptyLabel();
              }
              return isFirst = false;
            }
          });
        });
      });
    }
  });

}).call(this);
