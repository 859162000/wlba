require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/tab', 'model/financingTable'], ($, _, ko, backend, tab, table)->
  $ document
  .ready ->
    class viewModel
      constructor: ->
        self = this

        self.financingTable = new table.viewModel
          events:
            sortHandler: (column, order)->
              field = column.field
              if order != 'asc'
                field = '-' + column.field
              self.orderBy field

        self.orderBy = ko.observable('-max_expected_profit_rate')
        self.filters = ko.observable()

        self.tabTree =
          tabs:[
            {
              name: '按起购金额'
            }
            {
              name: '按产品期限'
            }
            {
              name: '按收益类型'
            }
          ]

          subTabs:[
            [
              name: '10万以下'
              values:
                lt_threshold: 10
            ,
              name: '10万-20万'
              values:
                gte_threshold: 10
                lt_threshold: 20
            ,
              name: '20万以上'
              values:
                gte_threshold: 20
            ]
            [
              name: '3个月以下'
              values:
                lt_period: 3
            ,
              name: '3-6个月'
              values:
                gte_period: 3
                lt_period: 6
            ,
              name: '6-12个月'
              values:
                gte_period: 6
                lt_period: 12
            ,
              name: '1年以上'
              values:
                gte_period: 12
            ]
            [
              name: '保本固定收益'
              values:
                profit_type: '保本固定收益'
            ,
              name: '保本浮动收益'
              values:
                profit_type: '保本浮动收益'
            ,
              name: '非保本浮动收益'
              values:
                profit_type: '非保本浮动收益'
            ]
          ]

        self.subTab = new tab.viewModel()

        self.tab = new tab.viewModel
          tabs: self.tabTree.tabs
          events:
            tabSelected: (data, event)->
              index = _.indexOf self.tabTree.tabs, data
              self.subTab.data
                tabs: self.tabTree.subTabs[index]
                events:
                  tabSelected: (data, event)->
                    self.filters data.values

        ko.computed ()->
          backend.loadData 'financings',
            _.extend {
              page_size: 10
              ordering: self.orderBy()
            }, self.filters()
          .done (data)->
            self.financingTable.data(data.results)

    ko.applyBindings new viewModel()
