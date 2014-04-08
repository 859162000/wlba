// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      knockout: 'lib/knockout-3.0.0'
    }
  });

  require(['jquery', 'underscore', 'knockout', 'lib/backend', 'model/fund', 'model/fundTable', 'lib/filter'], function($, _, ko, backend, fund, table, filter) {
    var DataViewModel, viewModel;
    DataViewModel = (function() {
      function DataViewModel() {
        var self;
        self = this;
        self.tabTree = filter.arrayToFilter(['混合型', '结构型', '债券型', '理财型', '指数型', '保本型', '封闭式', 'QDII', '股票型', '货币型'], 'type', '全部');
        self.selectedTab = ko.observable(self.tabTree[0]);
        self.fundTable = new table.viewModel({});
        ko.computed(function() {
          var params;
          params = _.extend({
            count: 10
          }, self.selectedTab().values);
          return backend.loadData('funds', params).done(function(data) {
            return backend.joinFavorites(data, 'funds', self.fundTable, function(data) {
              return _.map(data.results, function(item) {
                return new fund.viewModel({
                  data: item
                });
              });
            });
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
