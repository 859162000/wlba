require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'
    'jquery.purl': 'lib/purl'
  shim:
    'jquery.purl': ['jquery']

require ['jquery', 'underscore', 'knockout', 'jquery.purl', 'lib/backend', 'model/fund'], ($, _, ko, purl, backend, fund)->
  class ViewModel
    constructor: ()->
      self = this

      asset_param = parseInt(purl(document.location.href).param('asset'))
      if isNaN(asset_param) or asset_param == 0
        asset_param = 30

      self.asset = ko.observable(asset_param)

      self.trusts = ko.observable []
      self.financings = ko.observable []
      self.funds = ko.observable []

      self.activeFilters = ko.observableArray()
      self.clickOnFilter = (value, event)->
        context = ko.contextFor(event.target)
        if self.activeFilters.indexOf(value) >= 0
          return

        _.each context.$parent.values, (value)->
          self.activeFilters.remove value

        self.activeFilters.push value

      self.filters = [
        {
          name : '销售状态'
          values: [
            {
              name: '不限'
              values: null
            }
            {
              name: '在售'
              values:
                status: '在售'
            }
            {
              name: '预售'
              values:
                status: '预售'
            }
            {
              name: '停售'
              values:
                status: '停售'
            }
          ]
        }
        {
          name: '产品类型'
          values: [
            {
              name: '不限'
              values: null
            }
            {
              name: '信托产品'
              values:
                type: 'trusts'
            }
            {
              name: '银行理财'
              values:
                type: 'bank_financings'
            }
            {
              name: '基金产品'
              values:
                type: 'funds'
            }
          ]
        }
        {
          name: '年化收益'
          values: [
            {
              name: '不限'
              values: null
            }
            {
              name: '4%以下'
              values:
                max_rate: 4
            }
            {
              name: '4%-6%'
              values:
                min_rate: 4
                max_rate: 6
            }
            {
              name: '6%-8%'
              values:
                min_rate: 6
                max_rate: 8
            }
            {
              name: '8%-10%'
              values:
                min_rate: 8
                max_rate: 10
            }
            {
              name: '10%-15%'
              values:
                min_rate: 10
                max_rate: 15
            }
            {
              name: '15%以上'
              values:
                min_rate: 15
            }
          ]
        }
      ]

      _.each self.filters, (value, index)->
        self.activeFilters.push value.values[0]

      ko.computed ()->
        params = _.reduce(self.activeFilters(), ((memo, value)-> _.extend(memo, value.values)), {page_size: 5, lte_threshold: self.asset()})

        self.trusts([])
        self.financings([])
        self.funds([])

        types = ['trusts', 'bank_financings', 'funds']
        if _.has params, 'type'
          types = [params.type]

        delete params.type

        _.each types, (value)->

          backend.loadData value, params
          .done (data)->
            if value == 'trusts'
              self.trusts(data.results)
            else if value == 'bank_financings'
              self.financings(data.results)
            else if value == 'funds'
              funds = _.map data.results, (item)->
                new fund.viewModel
                  data: item
              self.funds(funds)
      .extend({throttle: 1})

  viewModel = new ViewModel()
  ko.applyBindings viewModel