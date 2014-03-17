require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/cash', 'model/pager'], ($, _, ko, backend, cash, pager)->
  $ document
  .ready ->
    class DataViewModel
      constructor: ->
        self = this
        self.products = ko.observable()
        self.pager = new pager.viewModel

        self.activeFilters = ko.observableArray()

        self.clickOnFilter = (value, event)->
          context = ko.contextFor(event.target)

          if self.activeFilters.indexOf(value) >= 0
            return

          _.each context.$parent.values, (value)->
            self.activeFilters.remove value

          self.activeFilters.push value

          # Any filter change reset page number to 1
          self.pager.currentPageNumber(1)

        self.queryData = ()->
          filters = _.chain(self.activeFilters()).pluck('values').flatten().compact().value()
          params = _(filters).reduce ((result, object)-> _.extend(result, object)), {page: self.pager.currentPageNumber()}

          if console?
            console.log 'loading data'
          backend.loadData 'cashes', params
          .done( (data)->
            self.products data.results
            self.pager.totalPageNumber data.num_pages
          ).fail( (xhr, status, error)->
            alert(status + error)
          )

        self.filters = [
          {
            name : '销售状态'
            values: [
              {
                name: '不限'
                values: null
              }
              {
                name: '开放'
                values: [
                  status: '开放'
                ]
              }
              {
                name: '关闭'
                values: [
                  status: '关闭'
                ]
              }
           ]
          },
          {
            name : '投资期限'
            values: [
              {
                name: '不限'
                values: null
              }
              {
                name: '活期'
                values: [
                  period: 0
                ]
              }
              {
                name: '3个月以内'
                values: [
                  gt_period: 0
                  lte_period: 3
                ]
              }
              {
                name: '3-6个月'
                values: [
                  gt_period: 3
                  lte_period: 6
                ]
              }
              {
                name: '6-12个月'
                values: [
                  gt_period: 6
                  lte_period: 12
                ]
              }
              {
                name: '1-3年'
                values: [
                  gt_period: 12
                  lte_period: 36
                ]
              }
              {
                name: '3年以上'
                values: [
                  gt_period: 36
                ]
              }
           ]
          }
        ]

        _.each self.filters, (value)->
          self.activeFilters.push value.values[0]

        ko.computed ()->
          self.queryData()
        .extend {throttle: 1}

    viewModel = new DataViewModel()
    ko.applyBindings viewModel