// Generated by CoffeeScript 1.7.1
(function() {
  define(['knockout', 'underscore'], function(ko, _) {
    var viewModel;
    viewModel = (function() {
      viewModel.prototype.titleWidthPercent = 10;

      function viewModel(context) {
        var data, self;
        self = this;
        data = context.data;
        self.name = ko.observable(data.name);
        self.products = ko.observableArray(data.products);
        if (context && _.has(context, 'asset')) {
          self.asset = context.asset;
        } else {
          self.asset = ko.observable(100);
        }
        self.events = {};
        if (_.has(context, 'events')) {
          self.events = _.extend(self.events, context.events);
        }
        self.productSelected = function(product) {
          if (_.has(self.events, 'productSelected')) {
            return self.events.productSelected(product);
          } else {
            return console.log(product);
          }
        };
      }

      viewModel.prototype.data = function(data) {
        this.name(data.name);
        return this.products(data.products);
      };

      viewModel.prototype.productDescription = function(productEntry) {
        var amount, asset, percent;
        percent = 0;
        amount = 0;
        asset = this.asset();
        if (productEntry.type === 'percent') {
          percent = productEntry.value;
          amount = percent / 100 * asset;
        } else {
          amount = productEntry.value;
          percent = amount / asset * 100;
        }
        return amount.toFixed(0) + '万 ' + percent.toFixed(0) + '%';
      };

      viewModel.prototype.productWidth = function(productEntry) {
        return (100 - this.titleWidthPercent) / this.products().length + '%';
      };

      return viewModel;

    })();
    return {
      viewModel: viewModel
    };
  });

}).call(this);

//# sourceMappingURL=portfolio.map
