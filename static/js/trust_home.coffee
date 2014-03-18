require.config
  paths:
    jquery: 'lib/jquery.min'
    knockout: 'lib/knockout-3.0.0'
    underscore: 'lib/underscore-min'

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/tab', 'model/trustTable'], ($, _, ko, backend, tab, table)->
  $(document).ready ->
    class DataViewModel
      constructor: ->
        self = this

        self.trustTable = new table.viewModel {}

        self.filteredTable = new table.viewModel
          events:
            sortHandler: (column, order)->
              field = column.field
              if _.has(column, 'remote_field')
                field = column.remote_field
              if order == 'dsc'
                field = '-' + field
              self.orderBy field

        self.orderBy = ko.observable('-issue-date')
        self.filters = ko.observable()

        self.tabTree =
          tabs:[
            name: '按期限'
          ,
            name: '按起点'
          ,
            name: '按收益'
          ]
          subTabs: [
            [
              name: '12个月以内'
              values:
                max_period: 12
            ,
              name: '12个月-24个月'
              values:
                min_period: 12
                max_period: 24
            ,
              name: '24个月以上'
              values:
                min_period: 24
            ]
            [
              name: '100万以下'
              values:
                'max_threshold': 100.0
            ,
              name: '100万-300万'
              values:
                min_threshold: 100.0
                max_threshold: 300.0
            ,
              name: '300万以上'
              values:
                min_threshold: 300
            ]
            [
              name: '13%以上'
              values:
                min_rate: 13
            ,
              name: '10%-13%'
              values:
                min_rate: 10
                max_rate: 13
            ,
              name: '低于10%'
              values:
                max_rate: 10
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
                    self.filters(
                      _.extend data.values,
                        page_size: 10
                    )


        ko.computed ()->
          backend.loadData 'trusts',
            _.extend self.filters(), ordering: self.orderBy()
          .done (data)->
            self.filteredTable.data(data.results)
          .fail ->
            alert '发生网络问题 加载内容失败'


    model = new DataViewModel()
    ko.applyBindings(model)

    backend.loadData 'trust',
      count: 10
      ordering: '-issue_date'
    .done (data)->
        model.trustTable.data(data.results)
