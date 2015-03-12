// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      knockout: 'lib/knockout'
    }
  });

  require(['jquery', 'underscore', 'knockout', 'lib/backend', 'model/pager', 'model/fundTable', 'model/fund', 'lib/filter'], function($, _, ko, backend, pager, table, fund, filter) {
    var DataViewModel, viewModel;
    DataViewModel = (function() {
      function DataViewModel() {
        var self;
        self = this;
        self.fundTable = new table.viewModel({
          events: {
            sortHandler: function(column, order) {
              var field;
              field = column.field;
              if (order === 'dsc') {
                field = '-' + field;
              }
              return self.orderBy(field);
            }
          }
        });
        self.orderBy = ko.observable();
        self.orderBy('-rate_7_days');

        /*
        Pager
         */
        self.pager = new pager.viewModel();

        /*
        The filters
         */
        self.activeFilters = ko.observableArray([]);
        self.isFilterActive = function(value) {
          return self.activeFilters.indexOf(value) >= 0;
        };
        self.clickOnFilter = function(value, event) {
          var context;
          context = ko.contextFor(event.target);
          if (self.activeFilters.indexOf(value) >= 0) {
            return;
          }
          _.each(context.$parent.values, function(value) {
            return self.activeFilters.remove(value);
          });
          self.activeFilters.push(value);
          return self.pager.currentPageNumber(1);
        };
        self.filters = [
          {
            name: '基金类型',
            values: filter.arrayToFilter(['混合型', '结构型', '债券型', '理财型', '指数型', '保本型', '封闭式', 'QDII', '股票型', '货币型'], 'type')
          }, {
            name: '七日年化利率',
            values: [
              {
                name: '不限',
                values: null
              }, {
                name: '0%以下',
                values: [
                  {
                    'lt_rate_7_days': 0
                  }
                ]
              }, {
                name: '0%-3%',
                values: [
                  {
                    lt_rate_7_days: 3,
                    gte_rate_7_days: 0
                  }
                ]
              }, {
                name: '3%-6%',
                values: [
                  {
                    lt_rate_7_days: 6,
                    gte_rate_7_days: 3
                  }
                ]
              }, {
                name: '6%以上',
                values: [
                  {
                    gte_rate_7_days: 6
                  }
                ]
              }
            ]
          }, {
            name: '月涨幅',
            values: [
              {
                name: '不限',
                values: null
              }, {
                name: '0%以下',
                values: [
                  {
                    'lt_rate_1_month': 0
                  }
                ]
              }, {
                name: '0%-3%',
                values: [
                  {
                    lt_rate_1_month: 3,
                    gte_rate_1_month: 0
                  }
                ]
              }, {
                name: '3%-6%',
                values: [
                  {
                    lt_rate_1_month: 6,
                    gte_rate_1_month: 3
                  }
                ]
              }, {
                name: '6%以上',
                values: [
                  {
                    gte_rate_1_month: 6
                  }
                ]
              }
            ]
          }
        ];
        _.each(self.filters, function(value) {
          return self.activeFilters.push(value.values[0]);
        });
        ko.computed(function() {
          var filters, params;
          filters = _.chain(self.activeFilters()).pluck('values').flatten().compact().value();
          params = _(filters).reduce((function(result, object) {
            return _.extend(result, object);
          }), {
            page: self.pager.currentPageNumber(),
            ordering: self.orderBy()
          });
          return backend.loadData('funds', params).done(function(data) {
            backend.joinFavorites(data, "funds", self.fundTable, function(items) {
              return _.map(items.results, function(item) {
                return new fund.viewModel({
                  data: item
                });
              });
            });
            return self.pager.totalPageNumber(data.num_pages);
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
