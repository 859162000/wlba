// Generated by CoffeeScript 1.8.0
(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  define(['jquery', 'underscore', 'knockout'], function($, _, ko) {
    var viewModel;
    viewModel = (function() {
      function viewModel(context) {
        this.backEndRate = __bind(this.backEndRate, this);
        this.frontEndRate = __bind(this.frontEndRate, this);
        var self;
        self = this;
        if (_.has(context, 'data')) {
          _(self).extend(context['data']);
        }
      }

      viewModel.prototype.frontEndRate = function() {
        if (this.issue_front_end_charge_rates.length > 0) {
          return this.issue_front_end_charge_rates[0].value.toFixed(2) + '%';
        }
        return '--';
      };

      viewModel.prototype.backEndRate = function() {
        if (this.issue_back_end_charge_rates.length > 0) {
          return this.issue_back_end_charge_rates[0].value.toFixed(2) + '%';
        }
        return '--';
      };

      return viewModel;

    })();
    return {
      viewModel: viewModel
    };
  });

}).call(this);
