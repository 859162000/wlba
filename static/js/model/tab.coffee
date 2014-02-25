define ['jquery', 'underscore', 'knockout'], ($, _, ko)->
  class viewModel
    constructor: (context)->
      self = this

      self.tabs = ko.observableArray()
      self.selectedTab = ko.observable()

      self.events = {}

      @data context

    tabSelected: (data, event)=>
      @selectedTab data

      if _.has @events, 'tabSelected'
        @events.tabSelected data, event
      else
        console.log 'tab selected ' + data

    data: (context)=>
      if context
        if _.has context, 'events'
          _(@events).extend context.events

        if _.has context, 'tabs'
          @tabs context.tabs

          @tabSelected @tabs()[0]

  viewModel: viewModel