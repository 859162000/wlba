// Generated by CoffeeScript 1.7.1
(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(['jquery', 'underscore', 'model/table'], function($, _, table) {
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
              remote_field: 'issuer__short_name',
              field: 'issuer_short_name'
            }, {
              name: '',
              colspan: 1,
              text: function(item) {
                var link_text;
                link_text = '收藏';
                if (item.is_favorited === 1) {
                  link_text = '取消收藏';
                }
                return '<a class="button button-mini button-pink" onclick="addToFavorite(event, ' + "'trusts'" + ');" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">' + link_text + '</a>';
              }
            }, {
              name: '',
              colspan: 1,
              text: function(item) {
                return '<a class="button button-mini button-pink" href="/trust/detail/' + item.id + '">详情</a>';
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

    })(table.viewModel);
    return {
      viewModel: viewModel
    };
  });

}).call(this);

//# sourceMappingURL=trustTable.map
