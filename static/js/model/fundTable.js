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
              name: '代码',
              colspan: 2,
              field: 'product_code',
              text: function(item) {
                return item.product_code;
              }
            }, {
              name: '基金名称',
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
              field: 'rate_day',
              text: function(item) {
                return item.rate_day + '%';
              }
            }, {
              name: '近一月涨幅',
              colspan: 2,
              sortable: true,
              field: 'profit_rate_month',
              text: function(item) {
                return item.profit_rate_month + '%';
              }
            }, {
              name: '近三月涨幅',
              colspan: 2,
              sortable: true,
              field: 'profit_rate_3months',
              text: function(item) {
                return item.profit_rate_3months + '%';
              }
            }, {
              name: '近半年涨幅',
              colspan: 2,
              sortable: true,
              field: 'profit_rate_6months',
              text: function(item) {
                return item.profit_rate_6months + '%';
              }
            }, {
              name: '前端|后端费率',
              colspan: 2,
              text: function(item) {
                return item.frontEndRate() + '|' + item.backEndRate();
              }
            }, {
              name: '',
              colspan: 2,
              text: function(item) {
                return '<a class="button button-mini button-yellow" href="/fund/detail/' + item.id + '">详情</a>';
              }
            }
          ]
        };
        _.extend(context, defaultContext);
        viewModel.__super__.constructor.call(this, context);
      }

      return viewModel;

    })(table.viewModel);
    return {
      viewModel: viewModel
    };
  });

}).call(this);

//# sourceMappingURL=fundTable.map
