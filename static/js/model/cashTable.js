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
              name: '发行机构',
              colspan: 2,
              sortable: true,
              field: 'issuer__name',
              text: function(item) {
                return item.issuer_name;
              }
            }, {
              name: '期限',
              colspan: 2,
              sortable: true,
              field: 'period',
              text: function(item) {
                if (item.period) {
                  return item.period + '个月';
                } else {
                  return '活期';
                }
              }
            }, {
              name: '七日年化利率',
              colspan: 2,
              sortable: true,
              field: 'profit_rate_7days',
              text: function(item) {
                return item.profit_rate_7days + '%';
              }
            }, {
              name: '每万份收益',
              colspan: 2,
              sortable: true,
              field: 'profit_10000',
              text: function(item) {
                return item.profit_10000 + '元';
              }
            }, {
              name: '购买链接',
              colspan: 2,
              text: function(item) {
                return '<a href="' + item.buy_url + '">' + item.buy_text + '</a>';
              }
            }, {
              name: '收藏',
              colspan: 1,
              text: function(item) {
                var link_text;
                link_text = '收藏';
                if (item.is_favorited === 1) {
                  link_text = '取消';
                }
                return '<a class="button button-mini button-pink" onclick="addToFavorite(event,' + "'cashes');" + '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">' + link_text + '</a>';
              }
            }, {
              name: '详情',
              colspan: 1,
              text: function(item) {
                return '<a class="button button-mini button-pink" href="/cash/detail/' + item.id + '">详情</a>';
              }
            }
          ]
        };
        viewModel.__super__.constructor.call(this, _(defaultContext).extend(context));
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

//# sourceMappingURL=cashTable.map
