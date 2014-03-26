require.config
  paths:
    jquery: 'lib/jquery.min'
    knockout: 'lib/knockout-3.0.0'
    underscore: 'lib/underscore-min'

require ['jquery', 'knockout', 'underscore', 'lib/backend', 'model/fundTable', 'model/financingTable', 'model/trustTable', 'model/cashTable', 'model/tab'], ($, ko, _, backend, fund, financing, trust, cash, tab)->
  class viewModel
    constructor: ->
      self = this

      self.trustTable = new trust.viewModel {}
      self.cashTable = new cash.viewModel {}
      self.fundTable = new fund.viewModel {}
      self.financingTable = new financing.viewModel {}


      backend.loadFavorites 'trusts'
      .done (data)->
        self.trustTable.transform_favorite data

      backend.loadFavorites 'cashes'
      .done (data)->
          self.cashTable.transform_favorite data

      backend.loadFavorites 'funds'
      .done (data) ->
        self.fundTable.transform_favorite data

      backend.loadFavorites 'financings'
      .done (data) ->
        self.financingTable.transform_favorite data

  ko.applyBindings(new viewModel())
