// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      knockout: 'lib/knockout-3.0.0'
    }
  });

  require(['jquery', 'underscore', 'knockout', 'lib/backend', 'lib/templateLoader', 'model/portfolio', 'model/fund'], function($, _, ko, backend, templateLoader, portfolio) {
    return $(document).ready(function() {
      var DataViewModel, viewModel;
      DataViewModel = (function() {
        function DataViewModel() {
          var self;
          self = this;
          self.asset = ko.observable(300);
          self.riskScore = ko.observable(1);
          self.period = ko.observable(24);
          self.portfolio = ko.observable();
          ko.computed(function() {
            var params;
            params = {
              asset_min: self.asset(),
              asset_max: self.asset(),
              period_min: self.period(),
              period_max: self.period(),
              risk_score: self.riskScore()
            };
            return backend.loadPortfolio(params).done(function(data) {
              return self.portfolio(new portfolio.viewModel({
                data: data.results[0],
                asset: self.asset,
                events: {
                  productSelected: function(value) {
                    var amount, type;
                    type = value.product.name;
                    self.productsType(type);
                    amount = value.value;
                    if (value.type === 'percent') {
                      amount = amount / 100 * self.asset();
                    }
                    return self.amount(amount);
                  }
                }
              }));
            });
          });

          /*
          The filtered products related stuff
           */
          self.products = null;
          self.productsType = ko.observable();
          self.template_name = ko.observable();
          self.amount = ko.observable(0);
          ko.computed(function() {
            var amount, type;
            type = self.productsType();
            amount = self.amount();
            if (backend.isValidType(type)) {
              return backend.loadData(type, {
                count: 10,
                max_threshold: amount
              }).done(function(data) {
                self.products = data.results;
                if (self.products.length > 0) {
                  return self.template_name(templateLoader.template(type));
                } else {
                  return self.template_name('no-products-available');
                }
              });
            } else {
              if (typeof console !== "undefined" && console !== null) {
                console.log('The type not supported');
              }
              self.products = null;
              return self.template_name('no-products-available');
            }
          }).extend({
            throttle: 1
          });
        }

        return DataViewModel;

      })();
      viewModel = new DataViewModel();
      return ko.applyBindings(viewModel);
    });
  });

}).call(this);

//# sourceMappingURL=account_home.map
