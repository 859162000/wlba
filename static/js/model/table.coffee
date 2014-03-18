define ['jquery', 'underscore', 'knockout'], ($, _, ko)->
  class viewModel
    constructor: (context)->
      self = this

      self.columns = _(context.columns).map (item, index)->
        _({sortable: false}).extend(item)
      self.sortedColumn = ko.observable
        column: null
        order: 'asc'

      self.data = ko.observable()

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
        else
          self.sortedColumn {column: column, order: 'asc'}

        if _.has(self.events, 'sortHandler')
          self.events.sortHandler(column, order)

  viewModel: viewModel
