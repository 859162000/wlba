require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/fund', 'model/fundTable', 'lib/filter'], ($, _, ko, backend, fund, table, filter)->
  class DataViewModel
    constructor: ->
      self = this

      self.tabTree = filter.arrayToFilter ['混合型','结构型','债券型','理财型','指数型','保本型','封闭式','QDII','股票型','货币型'],
        'type', '全部'

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