// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      underscore: 'lib/underscore-min',
      knockout: 'lib/knockout-3.0.0'
    }
  });

  require(['jquery', 'underscore', 'knockout', 'lib/backend', 'model/tab', 'model/financingTable'], function($, _, ko, backend, tab, table) {
    return $(document).ready(function() {
      var viewModel;
      viewModel = (function() {
        function viewModel() {
          var self;
          self = this;
          self.financingTable = new table.viewModel({
            events: {
              sortHandler: function(column, order) {
                var field;
                field = column.field;
                if (_.has(column, 'remote_field')) {
                  field = column.remote_field;
                }
                if (order !== 'asc') {
                  field = '-' + column.field;
                }
                return self.orderBy(field);
              }
            }
          });
          self.orderBy = ko.observable('-max_expected_profit_rate');
          self.filters = ko.observable();
          self.tabTree = {
            tabs: [
              {
                name: '按起购金额'
              }, {
                name: '按产品期限'
              }, {
                name: '按收益类型'
              }
            ],
            subTabs: [
              [
                {
                  name: '10万以下',
                  values: {
                    lt_threshold: 10
                  }
                }, {
                  name: '10万-20万',
                  values: {
                    gte_threshold: 10,
                    lt_threshold: 20
                  }
                }, {
                  name: '20万以上',
                  values: {
                    gte_threshold: 20
                  }
                }
              ], [
                {
                  name: '3个月以下',
                  values: {
                    lt_period: 3
                  }
                }, {
                  name: '3-6个月',
                  values: {
                    gte_period: 3,
                    lt_period: 6
                  }
                }, {
                  name: '6-12个月',
                  values: {
                    gte_period: 6,
                    lt_period: 12
                  }
                }, {
                  name: '1年以上',
                  values: {
                    gte_period: 12
                  }
                }
              ], [
                {
                  name: '保本固定收益',
                  values: {
                    profit_type: '保本固定收益'
                  }
                }, {
                  name: '保本浮动收益',
                  values: {
                    profit_type: '保本浮动收益'
                  }
                }, {
                  name: '非保本浮动收益',
                  values: {
                    profit_type: '非保本浮动收益'
                  }
                }
              ]
            ]
          };
          self.subTab = new tab.viewModel();
          self.tab = new tab.viewModel({
            tabs: self.tabTree.tabs,
            events: {
              tabSelected: function(data, event) {
                var index;
                index = _.indexOf(self.tabTree.tabs, data);
                return self.subTab.data({
                  tabs: self.tabTree.subTabs[index],
                  events: {
                    tabSelected: function(data, event) {
                      return self.filters(data.values);
                    }
                  }
                });
              }
            }
          });
          ko.computed(function() {
            return backend.loadData('financings', _.extend({
              page_size: 10,
              ordering: self.orderBy()
            }, self.filters())).done(function(data) {
              return self.financingTable.data(data.results);
            });
          });
        }

        return viewModel;

      })();
      return ko.applyBindings(new viewModel());
    });
  });

}).call(this);

//# sourceMappingURL=financing_home.map
