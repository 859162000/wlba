// Generated by CoffeeScript 1.9.0
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
        self.selectedProduct = ko.observable();
        if (context && _.has(context, 'asset')) {
          self.asset = context.asset;
        } else {
          self.asset = ko.observable(100);
        }
        self.events = {};
        if (_.has(context, 'events')) {
          self.events = _.extend(self.events, context.events);
        }
        self.productSelected = (function(_this) {
          return function(product) {
            self.selectedProduct(product);
            if (_.has(self.events, 'productSelected')) {
              return self.events.productSelected(product, _this);
            } else {
              if (typeof console !== "undefined" && console !== null) {
                return console.log(product);
              }
            }
          };
        })(this);
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
        return (95 - this.titleWidthPercent) / this.products().length + '%';
      };

      return viewModel;

    })();
    return {
      viewModel: viewModel
    };
  });

}).call(this);

//# sourceMappingURL=portfolio.js.map
