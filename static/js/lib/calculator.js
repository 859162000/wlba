(function() {
  define(['jquery'], function($) {
    $('input[data-role=earning-calculator]').keyup(function(e) {
      var amount, earning, earning_element, earning_elements, i, period, periods, rate, target, unit, _len, _results;
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
      for (i = 0, _len = earning_elements.length; i < _len; i++) {
        earning_element = earning_elements[i];
        period = periods[i];
        earning = (rate / 100 * amount / 365 * period).toFixed(1);
        _results.push(earning && $.isNumeric(earning) ? $(earning_element).text(earning) : $(earning_element).text("0.0"));
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
      var amount, earning, earning_element, earning_elements, existing, i, target, total_amount, total_earning, _len, _results;
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
      for (i = 0, _len = earning_elements.length; i < _len; i++) {
        earning_element = earning_elements[i];
        _results.push(earning && $.isNumeric(earning) ? $(earning_element).text(earning) : $(earning_element).text("0.00"));
      }
      return _results;
    });
    return $('input[data-role=p2p-calculator]').keyup();
  });
}).call(this);
