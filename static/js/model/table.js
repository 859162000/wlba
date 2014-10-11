(function() {
  define(['jquery', 'underscore', 'knockout'], function($, _, ko) {
    var viewModel;
    viewModel = (function() {
      function viewModel(context) {
        var columns, self;
        self = this;
        columns = context.columns;
        if (_.has(context, 'fields')) {
          columns = _.filter(columns, function(data) {
            return _.contains(context.fields, data.name);
          });
        }
        self.columns = _(columns).map(function(item, index) {
          return _({
            sortable: false
          }).extend(item);
        });
        self.sortedColumn = ko.observable({
          column: null,
          order: 'asc'
        });
        self.data = ko.observable();
        self.isEmpty = ko.observable();
        self.colspan = ko.observable();
        self.colspan(_.reduce(self.columns, function(memo, column) {
          return memo + column.colspan;
        }, 0));
        self.events = {
          sortHandler: function(column, order) {
            var items;
            if (_.has(column, 'field')) {
              items = _.sortBy(self.data(), function(item) {
                return item[column.field];
              });
              if (order === 'asc') {
                return self.data(items);
              } else {
                return self.data(items.reverse());
              }
            }
          }
        };
        if (_.has(context, 'events')) {
          _(self.events).extend(context.events);
        }
        self.sortHandler = function(column) {
          var order, sortedColumn;
          sortedColumn = self.sortedColumn();
          order = 'asc';
          if (sortedColumn.column && sortedColumn.column.name === column.name) {
            if (sortedColumn.order === 'asc') {
              order = 'dsc';
            }
          }
          self.sortedColumn({
            column: column,
            order: order
          });
          if (_.has(self.events, 'sortHandler')) {
            return self.events.sortHandler(column, order);
          }
        };
      }
      return viewModel;
    })();
    return {
      viewModel: viewModel
    };
  });
}).call(this);
