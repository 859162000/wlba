// Generated by CoffeeScript 1.7.1
(function() {
  define(['jquery'], function($) {
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
      $(fee_element).text(fee);
      return $(actual_element).text(actual);
    });
    $('input[data-role=fee-calculator]').keyup();
    $('input[data-role=p2p-calculator]').keyup(function(e) {
      var amount, earning, earning_element, earning_elements, existing, i, target, total_amount, total_earning, _i, _len, _results;
      target = $(e.target);
      total_amount = parseFloat(target.attr('data-total-amount'));
      total_earning = parseFloat(target.attr('data-total-earning'));
      existing = parseFloat(target.attr('data-existing'));
      amount = parseFloat(target.val()) || 0;
      if (amount > target.attr('data-max')) {
        amount = target.attr('data-max');
        target.val(amount);
      }
      amount = parseFloat(existing) + parseFloat(amount);
      earning = ((amount / total_amount) * total_earning).toFixed(2);
      if (earning < 0) {
        earning = 0;
      }
      earning_elements = (target.attr('data-target')).split(',');
      _results = [];
      for (i = _i = 0, _len = earning_elements.length; _i < _len; i = ++_i) {
        earning_element = earning_elements[i];
        if (earning && $.isNumeric(earning)) {
          _results.push($(earning_element).text(earning));
        } else {
          _results.push($(earning_element).text("0.00"));
        }
      }
      return _results;
    });
    return $('input[data-role=p2p-calculator]').keyup();
  });

}).call(this);

//# sourceMappingURL=calculator.map
