// Generated by CoffeeScript 1.7.1
(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(['jquery', 'underscore', 'model/table', 'model/fund'], function($, _, table, fund) {
    var viewModel;
    viewModel = (function(_super) {
      __extends(viewModel, _super);

      function viewModel(context) {
        var defaultContext;
        defaultContext = {
          columns: [
            {
              name: '代码',
              colspan: 2,
              field: 'product_code',
              text: function(item) {
                return item.product_code;
              }
            }, {
              name: '名称',
              colspan: 3,
              sortable: true,
              field: 'name',
              text: function(item) {
                return item.name;
              }
            }, {
              name: '基金类型',
              colspan: 2,
              sortable: true,
              field: 'type',
              text: function(item) {
                return item.type;
              }
            }, {
              name: '单位净值',
              colspan: 2,
              sortable: true,
              field: 'face_value',
              text: function(item) {
                return item.face_value;
              }
            }, {
              name: '日涨幅',
              colspan: 2,
              sortable: true,
              field: 'rate_today',
              text: function(item) {
                return item.rate_today + '%';
              }
            }, {
              name: '近一月涨幅',
              colspan: 2,
              sortable: true,
              field: 'rate_1_month',
              text: function(item) {
                return item.rate_1_month + '%';
              }
            }, {
              name: '近三月涨幅',
              colspan: 2,
              sortable: true,
              field: 'rate_3_months',
              text: function(item) {
                return item.rate_3_months + '%';
              }
            }, {
              name: '近半年涨幅',
              colspan: 2,
              sortable: true,
              field: 'rate_6_months',
              text: function(item) {
                return item.rate_6_months + '%';
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
                return ' <a class="button button-mini button-white" onclick="addToFavorite(event,' + "'funds');" + '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">' + link_text + '</a>';
              }
            }, {
              name: '详情',
              colspan: 1,
              text: function(item) {
                return '<a class="button button-mini button-pink" href="/fund/detail/' + item.id + '">详情</a>';
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
          return new fund.viewModel({
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

//# sourceMappingURL=fundTable.map
