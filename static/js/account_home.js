(function() {
  var DataViewModel, viewModel;
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      knockout: 'lib/knockout',
      tools: 'lib/modal.tools'
    }
  });
  require(['jquery', 'underscore', 'knockout', 'lib/backend', 'lib/templateLoader', 'model/portfolio', 'tools', 'lib/jquery.number.min'], function($, _, ko, backend, templateLoader, portfolio, tool) {});
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
          lt_asset: self.asset(),
          min_period: self.period(),
          max_period: self.period(),
          risk_score: self.riskScore()
        };
        return backend.loadPortfolio(params.done(function(data) {
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
        }));
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
          }.done(function(data) {
            self.products = data.results;
            if (self.products.length > 0) {
              return self.template_name(templateLoader.template(type));
            } else {
              return self.template_name('no-products-available');
            }
          }));
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
  ko.applyBindings(viewModel);
  backend.fundInfo().done(function(data) {
    var totalAsset;
    totalAsset = parseFloat($("#total_asset").attr("data-p2p")) + parseFloat(data["fund_total_asset"]);
    $("#total_asset").text($.number(totalAsset, 2));
    $("#fund_total_asset").text($.number(data["fund_total_asset"], 2));
    $("#fund_total_asset_title").text($.number(data["fund_total_asset"], 2));
    $("#total_income").text($.number(data["total_income"], 2));
    $("#fund_income_week").text($.number(data["fund_income_week"], 2));
    $("#fund_income_month").text($.number(data["fund_income_month"], 2));
  }).fail(function(data) {
    return tool.modalAlert({
      title: '温馨提示',
      msg: '基金获取失败，请刷新重试！',
      callback_ok: function() {
        return location.reload();
      }
    });
  });
  return;
}).call(this);
