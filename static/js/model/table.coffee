define ['jquery', 'underscore', 'knockout'], ($, _, ko)->
  class viewModel
    constructor: (context)->
      self = this

      columns = context.columns
      if _.has context, 'fields'
        columns = _.filter columns, (data)->
          _.contains context.fields, data.name

      self.columns = _(columns).map (item, index)->
        _(
          {
            sortable: false
          }
        ).extend(item)
      self.sortedColumn = ko.observable
        column: null
        order: 'asc'

      self.data = ko.observable()
      self.isEmpty = ko.observable()
      self.colspan = ko.observable()

      self.colspan _.reduce(self.columns, (memo, column)->
                      return memo + column.colspan
                    ,0)

      self.events = {
        sortHandler: (column, order)->
          if _.has(column, 'field')
            items = _.sortBy(self.data(), (item)->
                item[column.field]
            )
            if order == 'asc'
              self.data items
            else
              self.data items.reverse()
      }

      if _.has(context, 'events')
        _(self.events).extend context.events

      self.sortHandler = (column)->
        sortedColumn = self.sortedColumn()
        order = 'asc'
        if sortedColumn.column && sortedColumn.column.name == column.name
          order = 'dsc' if sortedColumn.order == 'asc'

        self.sortedColumn {column: column, order: order}

        if _.has(self.events, 'sortHandler')
          self.events.sortHandler(column, order)

  viewModel: viewModel
