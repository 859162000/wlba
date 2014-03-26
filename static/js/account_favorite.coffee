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

      self.tabTree =
        tabs:[
          name: '信托'
          value: {
            type: 'trusts'
            table: self.trustTable
          }
        ,
          name: '银行理财'
          value: {
            type: 'financings'
            table: self.financingTable
          }
        ,
          name: '基金'
          value: {
            type: 'funds'
            table: self.fundTable
          }
        ,
          name: '现金类理财'
          value: {
            type: 'cashes'
            table: self.cashTable
          }
        ]

      self.type = ko.observable()
      self.dataTable = ko.observable()

      self.tab = new tab.viewModel
        tabs: self.tabTree.tabs
        events:
          tabSelected: (data, event)->
            self.dataTable data.value.table
            self.type data.value.type

      ko.computed ()->
        backend.loadFavorites(self.type())
        .done (data)->
            self.dataTable().transform_favorite(data)

  ko.applyBindings(new viewModel())
