// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      knockout: 'lib/knockout',
      'jquery.purl': 'lib/purl'
    },
    shim: {
      'jquery.purl': ['jquery']
    }
  });

  require(['jquery', 'underscore', 'knockout', 'jquery.purl', 'lib/backend', 'model/fund'], function($, _, ko, purl, backend, fund) {
    var ViewModel, viewModel;
    ViewModel = (function() {
      function ViewModel() {
        var asset_param, self;
        self = this;
        asset_param = parseInt(purl(document.location.href).param('asset'));
        if (isNaN(asset_param) || asset_param === 0) {
          asset_param = 30;
        }
        self.asset = ko.observable(asset_param);
        self.trusts = ko.observable([]);
        self.financings = ko.observable([]);
        self.funds = ko.observable([]);
        self.activeFilters = ko.observableArray();
        self.clickOnFilter = function(value, event) {
          var context;
          context = ko.contextFor(event.target);
          if (self.activeFilters.indexOf(value) >= 0) {
            return;
          }
          _.each(context.$parent.values, function(value) {
            return self.activeFilters.remove(value);
          });
          return self.activeFilters.push(value);
        };
        self.filters = [
          {
            name: '销售状态',
            values: [
              {
                name: '不限',
                values: null
              }, {
                name: '在售',
                values: {
                  status: '在售'
                }
              }, {
                name: '预售',
                values: {
                  status: '预售'
                }
              }, {
                name: '停售',
                values: {
                  status: '停售'
                }
              }
            ]
          }, {
            name: '产品类型',
            values: [
              {
                name: '不限',
                values: null
              }, {
                name: '信托产品',
                values: {
                  type: 'trusts'
                }
              }, {
                name: '银行理财',
                values: {
                  type: 'bank_financings'
                }
              }, {
                name: '基金产品',
                values: {
                  type: 'funds'
                }
              }
            ]
          }, {
            name: '年化收益',
            values: [
              {
                name: '不限',
                values: null
              }, {
                name: '4%以下',
                values: {
                  max_rate: 4
                }
              }, {
                name: '4%-6%',
                values: {
                  min_rate: 4,
                  max_rate: 6
                }
              }, {
                name: '6%-8%',
                values: {
                  min_rate: 6,
                  max_rate: 8
                }
              }, {
                name: '8%-10%',
                values: {
                  min_rate: 8,
                  max_rate: 10
                }
              }, {
                name: '10%-15%',
                values: {
                  min_rate: 10,
                  max_rate: 15
                }
              }, {
                name: '15%以上',
                values: {
                  min_rate: 15
                }
              }
            ]
          }
        ];
        _.each(self.filters, function(value, index) {
          return self.activeFilters.push(value.values[0]);
        });
        ko.computed(function() {
          var params, types;
          params = _.reduce(self.activeFilters(), (function(memo, value) {
            return _.extend(memo, value.values);
          }), {
            page_size: 5,
            lte_threshold: self.asset()
          });
          self.trusts([]);
          self.financings([]);
          self.funds([]);
          types = ['trusts', 'bank_financings', 'funds'];
          if (_.has(params, 'type')) {
            types = [params.type];
          }
          delete params.type;
          return _.each(types, function(value) {
            return backend.loadData(value, params).done(function(data) {
              var funds;
              if (value === 'trusts') {
                return self.trusts(data.results);
              } else if (value === 'bank_financings') {
                return self.financings(data.results);
              } else if (value === 'funds') {
                funds = _.map(data.results, function(item) {
                  return new fund.viewModel({
                    data: item
                  });
                });
                return self.funds(funds);
              }
            });
          });
        }).extend({
          throttle: 1
        });
      }

      return ViewModel;

    })();
    viewModel = new ViewModel();
    return ko.applyBindings(viewModel);
  });

}).call(this);

//# sourceMappingURL=products_search.map
