define ['underscore', 'knockout'], (_, ko)->
  class viewModel
    constructor: (context)->
      self = this

      self.totalPageNumber = ko.observable(10)
      self._currentPageNumber = ko.observable(1)

      self.events = {}
      if context and _.has(context, 'events')
        _(self.events).extend(context.events)

    pageNumberChanged: (data, event)=>
      if data > 0 and data <= @totalPageNumber()
        @_currentPageNumber(data)
        if _.has(@events, 'pageNumberChanged')
          @events.pageNumberChanged(data, event)
        else
          if console?
            console.log 'page number changed: ' + data

    # setter
    currentPageNumber: (data)=>
      if data
        @pageNumberChanged data
      else
        @_currentPageNumber()

    decreasePageNumber: (data, event)=>
      @currentPageNumber(@_currentPageNumber() - 1)

    increasePageNumber: (data, event)=>
      @currentPageNumber(@_currentPageNumber() + 1)


  viewModel: viewModel
