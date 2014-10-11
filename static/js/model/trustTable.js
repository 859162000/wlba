(function() {
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  define(['jquery', 'underscore', 'model/table'], function($, _, table) {
    var viewModel;
    viewModel = (function() {
      __extends(viewModel, table.viewModel);
      function viewModel(context) {
        var defaultContext;
        defaultContext = {
          columns: [
            {
              name: '序号',
              colspan: 1,
              text: function(item, index) {
                return index + 1;
              }
            }, {
              name: '名称',
              colspan: 3,
              text: function(item) {
                return '<a target="_blank" href="/trust/detail/' + item.id + '">' + item.short_name + '</a>';
              }
            }, {
              name: '状态',
              colspan: 1,
              sortable: true,
              field: 'status',
              text: function(item) {
                return item.status;
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
              name: '期限',
              colspan: 1,
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
              remote_field: 'issuer__short_name',
              field: 'issuer_short_name'
            }, {
              name: '收藏',
              colspan: 1,
              text: function(item) {
                if (item.is_favorited === 1) {
                  return '<a class="button-small button-white button-no-border" onclick="addToFavorite(event,' + "'trusts');" + '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">取消</a>';
                } else {
                  return '<a class="button-small button-white" onclick="addToFavorite(event,' + "'trusts');" + '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">收藏</a>';
                }
              }
            }, {
              name: '详情',
              colspan: 1,
              text: function(item) {
                return '<a target="_blank" class="button-small button-pink" href="/trust/detail/' + item.id + '">详情</a>';
              }
            }
          ]
        };
        _.extend(context, defaultContext);
        viewModel.__super__.constructor.call(this, context);
      }
      viewModel.prototype.transform_favorite = function(products) {
        var items;
        items = _.pluck(products.results, 'item');
        _.each(items, function(item) {
          return item.is_favorited = 1;
        });
        return this.data(items);
      };
      return viewModel;
    })();
    return {
      viewModel: viewModel
    };
  });
}).call(this);
