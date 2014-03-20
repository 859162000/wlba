// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      knockout: 'lib/knockout-3.0.0'
    }
  });

  require(['jquery', 'underscore', 'knockout', 'lib/backend', 'model/fund', 'model/fundTable'], function($, _, ko, backend, fund, table) {
    var DataViewModel, viewModel;
    DataViewModel = (function() {
      function DataViewModel() {
        var self;
        self = this;
        self.tabTree = [
          {
            name: '全部'
          }, {
            name: '股票型',
            values: {
              type: '股票型'
            }
          }, {
            name: '债券型',
            values: {
              type: '债券型'
            }
          }, {
            name: '货币型',
            values: {
              type: '货币型'
            }
          }, {
            name: '混合型',
            values: {
              type: '混合型'
            }
          }, {
            name: '保本型',
            values: {
              type: '保本型'
            }
          }, {
            name: '短期理财',
            values: {
              type: '短期理财'
            }
          }
        ];
        self.selectedTab = ko.observable(self.tabTree[0]);
        self.fundTable = new table.viewModel({});
        ko.computed(function() {
          var params;
          params = _.extend({
            count: 10
          }, self.selectedTab().values);
          return backend.loadData('funds', params).done(function(data) {
            return self.fundTable.data(_.map(data.results, function(item) {
              return new fund.viewModel({
                data: item
              });
            }));
          });
        }).extend({
          throttle: 1
        });
      }

      return DataViewModel;

    })();
    viewModel = new DataViewModel();
    return ko.applyBindings(viewModel);
  });

}).call(this);

//# sourceMappingURL=fund_home.map
