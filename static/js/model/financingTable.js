// Generated by CoffeeScript 1.7.1
(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(['jquery', 'underscore', 'model/table', 'model/financing'], function($, _, table, financing) {
    var viewModel;
    viewModel = (function(_super) {
      __extends(viewModel, _super);

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
              sortable: true,
              field: 'short_name',
              text: function(item) {
                return '<a target="_blank" href="/financing/detail/' + item.id + '">' + item.short_name + '</a>';
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
              name: '起购金额',
              colspan: 2,
              sortable: true,
              field: 'investment_threshold',
              text: function(item) {
                return item.investment_threshold + '万';
              }
            }, {
              name: '发行银行',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.bank_name;
              },
              field: 'bank_name',
              remote_field: 'bank__name'
            }, {
              name: '管理期限',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.period + '天';
              },
              field: 'period'
            }, {
              name: '收益类型',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.profit_type;
              },
              field: 'profit_type'
            }, {
              name: '预期收益',
              colspan: 2,
              sortable: true,
              text: function(item) {
                return item.expected_rate + '%';
              },
              field: 'expected_rate'
            }, {
              name: '收藏',
              colspan: 1,
              text: function(item) {
                if (item.is_favorited === 1) {
                  return '<a class="button button-mini button-white button-no-border" onclick="addToFavorite(event,' + "'financings');" + '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">取消</a>';
                } else {
                  return '<a class="button button-mini button-white" onclick="addToFavorite(event,' + "'financings');" + '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">收藏</a>';
                }
              }
            }, {
              name: '详情',
              colspan: 1,
              text: function(item) {
                return '<a target="_blank" class="button button-mini button-pink" href="/financing/detail/' + item.id + '">详情</a>';
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
        return this.data(_.map(items, function(item) {
          return new financing.viewModel({
            data: item
          });
        }));
      };

      return viewModel;

    })(table.viewModel);
    return {
      viewModel: viewModel
    };
  });

}).call(this);

//# sourceMappingURL=financingTable.map
