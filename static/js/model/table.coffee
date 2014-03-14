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

      self.events = {}

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
