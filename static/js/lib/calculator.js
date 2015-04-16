// Generated by CoffeeScript 1.8.0
(function() {
  define(['jquery'], function($) {
    var calculate;
    calculate = function(amount, rate, period, pay_method) {
      var result, term_amount;
      if (/等额本息/ig.test(pay_method)) {
        term_amount = amount * (rate * Math.pow(1 + rate, period)) / (Math.pow(1 + rate, period)(-1));
        result = term_amount * period - amount;
      } else if (/日计息/ig.test(pay_method)) {
        result = amount * (rate / 360) * period;
      } else {
        result = amount * (rate / 12) * period;
      }
      return result.toFixed(2);
    };
    $('input[data-role=earning-calculator]').keyup(function(e) {
      var amount, earning, earning_element, earning_elements, i, period, periods, rate, target, unit, _i, _len, _results;
      target = $(e.target);
      rate = target.attr('data-rate');
      periods = (target.attr('data-period')).split(',');
      amount = target.val();
      unit = target.attr('data-unit');
      if (unit) {
        amount = amount * unit;
      } else {
        amount = amount * 10000;
      }
      earning_elements = (target.attr('data-target')).split(',');
      _results = [];
      for (i = _i = 0, _len = earning_elements.length; _i < _len; i = ++_i) {
        earning_element = earning_elements[i];
        period = periods[i];
        earning = (rate / 100 * amount / 365 * period).toFixed(1);
        if (earning && $.isNumeric(earning)) {
          _results.push($(earning_element).text(earning));
        } else {
          _results.push($(earning_element).text("0.0"));
        }
      }
      return _results;
    });
    $('input[data-role=fee-calculator]').keyup(function(e) {
      var actual, actual_element, amount, fee, fee_element, rate, target;
      target = $(e.target);
      rate = target.attr('data-rate');
      amount = target.val();
      fee_element = target.attr('data-target-fee');
      actual_element = target.attr('data-target-actual');
      fee = (rate * amount).toFixed(2);
      actual = (amount - fee).toFixed(2);
      if (fee && $.isNumeric(fee)) {
        $(fee_element).text(fee);
      } else {
        $(fee_element).text("0.00");
      }
      if (actual && $.isNumeric(actual)) {
        return $(actual_element).text(actual);
      } else {
        return $(actual_element).text("0.00");
      }
    });
    $('input[data-role=fee-calculator]').keyup();
    $('input[data-role=p2p-calculator]').keyup(function(e) {
      var activity_rate, amount, earning, earning_element, earning_elements, existing, fee_earning, fee_element, fee_elements, fee_total_earning, i, pay_method, period, rate, target, total_amount, total_earning, _i, _j, _len, _len1, _results;
      target = $(e.target);
      total_amount = parseFloat(target.attr('data-total-amount'));
      total_earning = parseFloat(target.attr('data-total-earning'));
      fee_total_earning = parseFloat(target.attr('total-fee-earning'));
      existing = parseFloat(target.attr('data-existing'));
      period = target.attr('data-period');
      rate = target.attr('data-rate');
      rate = rate / 100;
      pay_method = target.attr('data-paymethod');
      activity_rate = target.attr('activity-rate');
      activity_rate = activity_rate / 100;
      amount = parseFloat(target.val()) || 0;
      if (amount > target.attr('data-max')) {
        amount = target.attr('data-max');
        target.val(amount);
      }
      amount = parseFloat(existing) + parseFloat(amount);
      earning = calculate(amount, rate, period, pay_method);
      fee_earning = calculate(amount, activity_rate, period, pay_method);
      if (earning < 0) {
        earning = 0;
      }
      earning_elements = (target.attr('data-target')).split(',');
      fee_elements = (target.attr('fee-target')).split(',');
      for (i = _i = 0, _len = earning_elements.length; _i < _len; i = ++_i) {
        earning_element = earning_elements[i];
        if (earning && $.isNumeric(earning)) {
          $(earning_element).text(earning);
        } else {
          $(earning_element).text("0.00");
        }
      }
      _results = [];
      for (i = _j = 0, _len1 = fee_elements.length; _j < _len1; i = ++_j) {
        fee_element = fee_elements[i];
        if (fee_earning && $.isNumeric(fee_earning)) {
          _results.push($(fee_element).text(fee_earning));
        } else {
          _results.push($(fee_element).text("0.00"));
        }
      }
      return _results;
    });
    return $('input[data-role=p2p-calculator]').keyup();
  });

}).call(this);
