$(document).ready ->
  DataViewModel = ->
    self = this

    self.trusts = ko.observable []

    ###
    Pager
    ###
    self.pageNumber = ko.observable 1

    # TODO Now limit the page number to 10 in code fix this later
    self.totalPageNumber = ko.observable 10

    self.setPageNumber = (data, event)->
      self.pageNumber(data)

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
      self.pageNumber(1)

    self.currentUrl = null

    # TODO fix this! Now the page loads will fire 2 requests for page 1
    # Root cause not founded yet.
    self.queryData = ()->
      filters = _.chain(self.activeFilters()).pluck('values').flatten().compact().value()
      params = _(filters).reduce ((result, object)-> _.extend(result, object)), {page: self.pageNumber()}
      queryString = $.param(params)
      url = 'http://127.0.0.1:8000/api/trusts/.jsonp?&ordering=-issue_date&' + queryString

      $.ajax(url, {
        dataType: 'jsonp'
      }).done( (data)->
        self.trusts data.results
        if data.num_pages > 10
          self.totalPageNumber 10
        else
          self.totalPageNumber data.num_pages
      ).fail( (xhr, status, error)->
        alert(status + error)
      )

    ko.computed ()->
      self.queryData()
    .extend {throttle: 1}

    # The filters
    self.filters = [
      {
        name: '资金门槛'
        values: [
          {
            name: '不限',
            values: null
          }
          {
            name: '50万以下'
            values: [
              max_threshold: 50
            ]
          }
          {
            name: '50-100万'
            values: [
              max_threshold: 100
              min_threshold: 50
            ]
          }
          {
            name: '100-300万'
            values: [
              min_threshold: 100
              max_threshold: 300
            ]
          }

        ]
      }
      {
        name: '产品期限'
        values: [
          {
            name: '不限'
            values: null
          }
          {
            name: '12个月以下'
            values:[
              max_period: 12
            ]
          }
          {
            name: '12-24个月'
            values:[
              min_period: 12
              max_period: 24
            ]
          }
          {
            name: '24-36个月'
            values:[
              min_period: 24
              max_period: 36
            ]
          }
          {
            name: '36个月以上'
            values: [
              min_period: 36
            ]
          }
        ]
      }
      {
        name: '预期收益'
        values: [
          {
            name: '不限'
            values: null
          }
          {
            name: '8%以下'
            values: [
              max_rate: 8
            ]
          }
          {
            name: '8%-10%'
            values: [
              min_rate: 8
              max_rate: 10
            ]
          }
          {
            name: '10%-15%'
            values: [
              min_rate: 10
              max_rate: 15
            ]
          }
          {
            name: '15%以上'
            values: [
              min_rate: 15
            ]
          }
        ]
      }
      {
        name: '收益分配'
        values:[
          {
            name: '不限'
            values: null
          }
          {
            name: '按月付息'
            values: [
              payment: '按月付息'
            ]
          }
          {
            name: '按季付息'
            values:[
              payment: '按季付息'
            ]
          }
          {
            name: '半年付息'
            values:[
              payment: '半年付息'
            ]
          }
          {
            name: '按年付息'
            values: [
              payment: '按年付息'
            ]
          }
          {
            name: '到期付息'
            values:[
              payment: '到期付息'
            ]
          }
        ]
      }
      {
        name: '抵(质)押率'
        values: [
          {
            name: '不限'
            values: null
          }
          {
            name: '30%以下'
            values:[
              max_mortgage_rate: 30
            ]
          }
          {
            name: '30%-50%'
            values:[
              min_mortgage_rate: 30
              max_mortgage_rate: 50
            ]
          }
          {
            name: '50%以上'
            values:[
              min_mortgage_rate: 50
            ]
          }
        ]
      }
      {
        name: '投资行业'
        values:[
          {
            name: '不限'
            values: null
          }
          {
            name: '房地产'
            values: [
              usage: '房地产'
            ]
          }
          {
            name: '金融'
            values: [
              usage: '金融'
            ]
          }
          {
            name: '基础设施'
            values: [
              usage: '基础设施'
            ]
          }
          {
            name: '工厂企业'
            values: [
              usage: '工厂企业'
            ]
          }
          {
            name: '工矿企业'
            values: [
              usage: '工矿企业'
            ]
          }
          {
            name: '其他'
            values: [
              usage: '其他'
            ]
          }
        ]
      }
      {
        name: '信托公司'
        width: '2' # 2 col spans
        fieldName: 'issuer_short_name'
        values: [
          {
            name: '不限'
            values: null
          }
          {
            name: '中信信托'
          }
          {
            name: '长安信托'
          }
          {
            name: '华信信托'
          }
          {
            name: '新华信托'
          }
          {
            name: '新时代信托'
          }
          {
            name: '湖南信托'
          }
          {
            name: '天融信托'
          }
          {
            name: '天津信托'
          }
          {
            name: '中行信托'
          }
          {
            name: '四川信托'
          }
          {
            name: '苏州信托'
          }
          {
            name: '更多'
          }
        ]
      }
    ]

    _.each self.filters, (value)->
      # push the first one as default, which is no filter
      self.activeFilters.push value.values[0]

    self

  viewModel = new DataViewModel()
  ko.applyBindings viewModel