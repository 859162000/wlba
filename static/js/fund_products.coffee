require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/pager', 'model/fundTable', 'model/fund'], ($, _, ko, backend, pager, table, fund)->
  class DataViewModel
    constructor: ()->
      self = this

      self.fundTable = new table.viewModel
        events:
          sortHandler: (column, order)->
            field = column.field
            if order == 'dsc'
              field = '-' + field
            self.orderBy(field)

      self.orderBy = ko.observable()

      ###
      Pager
      ###
      self.pager = new pager.viewModel()
      ###
      The filters
      ###
      self.activeFilters = ko.observableArray []

      self.isFilterActive = (value)->
        self.activeFilters.indexOf(value) >= 0

      self.clickOnFilter = (value, event)->
        context = ko.contextFor(event.target)

        if self.activeFilters.indexOf(value) >= 0
          return

        _.each context.$parent.values, (value)->
          self.activeFilters.remove value

        self.activeFilters.push value

        # Any filter change reset page number to 1
        self.pager.currentPageNumber(1)

      # The filters
      self.filters = [
        {
          name: '基金类型'
          values: [
            name: '不限',
            values: null
          ,
            name: '股票型'
            values: [
              type: '股票型'
            ]
          ,
            name: '债券型'
            values: [
              type: '债券型'
            ]
          ,
            name: '货币型'
            values: [
              type: '货币型'
            ]
          ,
            name: '混合型'
            values: [
              type: '混合型'
            ]
          ,
            name: '保本型'
            values: [
              type: '保本型'
            ]
          ,
            name: '短期理财'
            values: [
              type: '短期理财'
            ]
          ]
        }
        {
          name: '日涨幅'
          values: [
            {
              name: '不限'
              values: null
            }
            {
              name: '0%以下'
              values:[
                'lt_rate_today': 0
              ]
            }
            {
              name: '0%-3%'
              values:[
                lt_rate_today: 3
                gte_rate_today: 0
              ]
            }
            {
              name: '3%-6%'
              values:[
                lt_rate_today: 6
                gte_rate_today: 3
              ]
            }
            {
              name: '6%以上'
              values: [
                gte_rate_today: 6
              ]
            }
          ]
        }
        {
          name: '月涨幅'
          values: [
            {
              name: '不限'
              values: null
            }
            {
              name: '0%以下'
              values:[
                'lt_rate_1_month': 0
              ]
            }
            {
              name: '0%-3%'
              values:[
                lt_rate_1_month: 3
                gte_rate_1_month: 0
              ]
            }
            {
              name: '3%-6%'
              values:[
                lt_rate_1_month: 6
                gte_rate_1_month: 3
              ]
            }
            {
              name: '6%以上'
              values: [
                gte_rate_1_month: 6
              ]
            }
          ]
        }
      ]

      _.each self.filters, (value)->
        # push the first one as default, which is no filter
        self.activeFilters.push value.values[0]

      ko.computed ()->
        filters = _.chain(self.activeFilters()).pluck('values').flatten().compact().value()
        params = _(filters).reduce ((result, object)-> _.extend(result, object)),
          {
            page: self.pager.currentPageNumber()
            ordering: self.orderBy()
          }

        backend.loadData 'funds', params
        .done( (data)->
          backend.joinFavorites(data, "funds", self.fundTable, (items)->
            _.map(items.results, (item)->new fund.viewModel({data:item}))
          )
          self.pager.totalPageNumber data.num_pages
        ).fail( (xhr, status, error)->
          alert(status + error)
        )
      .extend {throttle: 1}
  viewModel = new DataViewModel()
  ko.applyBindings viewModel
