(function() {
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  define(['model/table'], function(table) {
    var viewModel;
    viewModel = (function() {
      __extends(viewModel, table.viewModel);
      function viewModel(context) {
        var defaultContext;
        defaultContext = {
          columns: [
            {
              name: '<p class="product-table-message">点击产品类别 查找符合条件的产品</p>',
              colspan: 1
            }
          ]
        };
        viewModel.__super__.constructor.call(this, _(defaultContext).extend(context));
      }
      return viewModel;
    })();
    return {
      viewModel: viewModel
    };
  });
}).call(this);
