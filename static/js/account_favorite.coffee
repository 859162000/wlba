require.config
  paths:
    jquery: 'lib/jquery.min'
    knockout: 'lib/knockout-3.0.0'
    underscore: 'lib/underscore-min'

require ['jquery', 'knockout', 'underscore', 'lib/backend', 'model/fund', 'model/financing', 'model/tab'], ($, ko, _, backend, fund, financing, tab)->
  class viewModel
    constructor: ->
      self = this

      self.trusts = ko.observable()
      self.funds = ko.observable()
      self.financings = ko.observable()


      backend.loadFavorites 'trusts'
      .done (data)->
        self.trusts(_.pluck(data.results, 'item'))

      backend.loadFavorites 'funds'
      .done (data) ->
        self.funds(_.pluck(data.results, 'item').map (element)->
          new fund.viewModel {
            data: element
          }
        )

      backend.loadFavorites 'financings'
      .done (data) ->
        self.financings(_.pluck(data.results, 'item').map (element)->
          new financing.viewModel {
            data: element
          }
        )

  ko.applyBindings(new viewModel())
