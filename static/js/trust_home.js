// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      knockout: 'lib/knockout-3.0.0',
      underscore: 'lib/underscore-min'
    }
  });

  require(['jquery', 'underscore', 'knockout', 'lib/backend', 'model/tab', 'model/table'], function($, _, ko, backend, tab, table) {
    return $(document).ready(function() {
      var DataViewModel, model;
      DataViewModel = (function() {
        function DataViewModel() {
          var self, trustColumns;
          self = this;
          trustColumns = [
            {
              name: '序号',
              colspan: 1,
              text: function(item, index) {
                return index + 1;
              }
            }, {
              name: '名称',
              colspan: 4,
              text: function(item) {
                return item.name;
              }
            }, {
              name: '资金门槛',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.investment_threshold + '万';
              },
              field: 'investment_threshold'
            }, {
              name: '产品期限',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.period + '个月';
              },
              field: 'period'
            }, {
              name: '预期收益',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.expected_earning_rate.toFixed(2) + '%';
              },
              field: 'expected_earning_rate'
            }, {
              name: '投资行业',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.usage;
              },
              field: 'usage'
            }, {
              name: '信托分类',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.type;
              },
              field: 'type'
            }, {
              name: '信托公司',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.issuer_short_name;
              },
              field: 'issuer_short_name'
            }, {
              name: '',
              colspan: 2,
              text: function(item) {
                return '<a class="button button-mini button-yellow" href="/trust/detail/' + item.id + '">详情</a>';
              }
            }
          ];
          self.trustTable = new table.viewModel({
            columns: trustColumns,
            events: {
              sortHandler: function(column, order) {
                var items;
                if (_.has(column, 'field')) {
                  items = _.sortBy(self.trustTable.data(), function(item) {
                    return item[column.field];
                  });
                  if (order === 'asc') {
                    return self.trustTable.data(items);
                  } else {
                    return self.trustTable.data(items.reverse());
                  }
                }
              }
            }
          });
          self.filteredTable = new table.viewModel({
            columns: trustColumns,
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
          self.orderBy = ko.observable('-issue-date');
          self.filters = ko.observable();
          self.tabTree = {
            tabs: [
              {
                name: '按期限'
              }, {
                name: '按起点'
              }, {
                name: '按收益'
              }
            ],
            subTabs: [
              [
                {
                  name: '12个月以内',
                  values: {
                    max_period: 12
                  }
                }, {
                  name: '12个月-24个月',
                  values: {
                    min_period: 12,
                    max_period: 24
                  }
                }, {
                  name: '24个月以上',
                  values: {
                    min_period: 24
                  }
                }
              ], [
                {
                  name: '100万以下',
                  values: {
                    'max_threshold': 100.0
                  }
                }, {
                  name: '100万-300万',
                  values: {
                    min_threshold: 100.0,
                    max_threshold: 300.0
                  }
                }, {
                  name: '300万以上',
                  values: {
                    min_threshold: 300
                  }
                }
              ], [
                {
                  name: '13%以上',
                  values: {
                    min_rate: 13
                  }
                }, {
                  name: '10%-13%',
                  values: {
                    min_rate: 10,
                    max_rate: 13
                  }
                }, {
                  name: '低于10%',
                  values: {
                    max_rate: 10
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
                      return self.filters(_.extend(data.values, {
                        page_size: 10
                      }));
                    }
                  }
                });
              }
            }
          });
          ko.computed(function() {
            return backend.loadData('trusts', _.extend(self.filters(), {
              ordering: self.orderBy()
            })).done(function(data) {
              return self.filteredTable.data(data.results);
            }).fail(function() {
              return alert('发生网络问题 加载内容失败');
            });
          });
        }

        return DataViewModel;

      })();
      model = new DataViewModel();
      ko.applyBindings(model);
      return backend.loadData('trust', {
        count: 10,
        ordering: '-issue_date'
      }).done(function(data) {
        return model.trustTable.data(data.results);
      });
    });
  });

}).call(this);

//# sourceMappingURL=trust_home.map
