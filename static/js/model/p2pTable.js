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
              name: '名称',
              colspan: 3,
              text: function(item) {
                return '<a target="_blank" class="blue" href="/p2p/detail/' + item.id + '">' + item.short_name + '</a>';
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
            }
          ]
        };
        _.extend(context, defaultContext);
        viewModel.__super__.constructor.call(this, context);
      }
      return viewModel;
    })();
    return {
      viewModel: viewModel
    };
  });
}).call(this);
