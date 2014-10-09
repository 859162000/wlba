(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      knockout: 'lib/knockout',
      underscore: 'lib/underscore-min'
    }
  });
  require(['jquery', 'underscore', 'knockout', 'lib/backend', 'model/tab', 'model/trustTable'], function($, _, ko, backend, tab, table) {
    var DataViewModel, model, trustId, trustName;
    DataViewModel = (function() {
      function DataViewModel() {
        var self;
        self = this;
        self.trustTable = new table.viewModel({});
        self.filteredTable = new table.viewModel({
          events: {
            sortHandler: function(column, order) {
              var field;
              field = column.field;
              if (_.has(column, 'remote_field')) {
                field = column.remote_field;
              }
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
            ordering: self.orderBy(),
            status: '在售'
          })).done(function(trusts) {
            return backend.joinFavorites(trusts, 'trusts', self.filteredTable);
          }).fail(function() {
            return alert('发生网络问题 加载内容失败');
          });
        });
      }
      return DataViewModel;
    })();
    model = new DataViewModel();
    ko.applyBindings(model);
    backend.loadData('trust', {
      count: 10,
      ordering: '-issue_date',
      status: '在售'
    }).done(function(trusts) {
      return backend.joinFavorites(trusts, "trusts", model.trustTable);
    });
    trustId = 0;
    trustName = '';
    $('.order-button').click(function(e) {
      e.preventDefault();
      trustId = $(e.target).attr('data-trust-id');
      trustName = $(e.target).attr('data-trust-name');
      return $(this).modal();
    });
    return $('#preorder_submit').click(function(event) {
      var name, phone;
      event.preventDefault();
      name = $('#name_input').val();
      phone = $('#phone_input').val();
      if (name && phone) {
        return backend.createPreOrder({
          product_url: trustId,
          product_type: 'trust',
          product_name: trustName,
          user_name: name,
          phone: phone
        }).done(function() {
          alert('预约成功，稍后我们的客户经理会联系您');
          $('#name_input').val('');
          $('#phone_input').val('');
          return $.modal.close();
        }).fail(function() {
          return alert('预约失败，请稍后再试或者拨打4008-588-066');
        });
      }
    });
  });
}).call(this);
