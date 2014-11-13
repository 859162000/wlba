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
              name: '类型',
              colspan: 1,
              text: function(item) {
                return item.mtype;
              }
            }, {
              name: '标题',
              colspan: 1,
              text: function(item) {
                return '<p class="blue" data-id="' + item.id + '">' + item.title(+'</p>' + '<p class="message-content">' + item.content(+'</p>'));
              }
            }, {
              name: '时间',
              colspan: 1,
              text: function(item) {
                return item.created_at;
              }
            }, {
              name: '&nbsp;',
              colspan: 1,
              text: function(item) {
                return '<span class="icon icon-msg-arrow-down" id="' + item.id(+'"></span>');
              }
            }
          ]
        };
        _.extend(context, defaultContext);
        viewModel.__super__.constructor.call(this, context);
        ({
          transform_message: function(msg) {
            var items;
            items = _.pluck(msg.data, 'item');
            _.each(items, function(item) {
              return item.is_read = 1;
            });
            return this.data(items);
          }
        });
      }

      return viewModel;

    })(table.viewModel);
    return {
      viewModel: viewModel
    };
  });

}).call(this);

//# sourceMappingURL=messageTable.map
