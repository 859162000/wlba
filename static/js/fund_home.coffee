require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/fund', 'model/fundTable'], ($, _, ko, backend, fund, table)->
  class DataViewModel
    constructor: ->
      self = this

      self.tabTree = [
        {
          name: '全部'
        }
        {
          name: '股票型'
          values:
            type: '股票型'
        }
        {
          name: '债券型'
          values:
            type: '债券型'
        }
        {
          name: '货币型'
          values:
            type: '货币型'
        }
        {
          name: '混合型'
          values:
            type: '混合型'
        }
        {
          name: '保本型'
          values:
            type:'保本型'
        }
        {
          name: '短期理财'
          values:
            type:'短期理财'
        }
      ]

      self.selectedTab = ko.observable(self.tabTree[0])
      self.fundTable = new table.viewModel {}

      ko.computed ()->
        params = _.extend {count:10}, self.selectedTab().values

        backend.loadData 'funds', params
        .done (data)->
          backend.joinFavorites(data, 'funds', self.fundTable, (data)->
              return _.map(data.results, (item)->
                  new fund.viewModel
                    data: item))
      .extend {throttle: 1}

  viewModel = new DataViewModel()
  ko.applyBindings viewModel