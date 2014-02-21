$ document
.ready ->
  class ViewModel
    constructor: ->
      self = this

      self.products = ko.observable([])

      ###
      Pager
      ###
      self.pageNumber = ko.observable 1

      # TODO Now limit the page number to 10 in code fix this later
      self.totalPageNumber = ko.observable 10

      self.setPageNumber = (data, event)->
        self.pageNumber(data)

      self.activeFilters = ko.observableArray()

      self.clickOnFilter = (value, event)->
        context = ko.contextFor(event.target)

        if self.activeFilters.indexOf(value) >= 0
          return

        _.each context.$parent.values, (value)->
          self.activeFilters.remove value

        self.activeFilters.push value

        # Any filter change reset page number to 1
        self.pageNumber(1)

      self.queryData = ()->
        filters = _.chain(self.activeFilters()).pluck('values').flatten().compact().value()
        params = _(filters).reduce ((result, object)-> _.extend(result, object)), {page: self.pageNumber()}
        queryString = $.param(params)
        url = 'http://127.0.0.1:8000/api/bank_financings/.jsonp?' + queryString

        console.log url

        $.ajax(url, {
          dataType: 'jsonp'
        }).done( (data)->
          self.products data.results
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
              values: [
                status: '在售'
              ]
            }
            {
              name: '预售'
              values: [
                status: '预售'
              ]
            }
            {
              name: '停售'
              values: [
                status: '停售'
              ]
            }
          ]
        }
        {
          name : '发行银行'
          values: [
            {
              name: '不限'
            }
            {
              name: '工商银行'
            }
            {
              name: '建设银行'
            }
            {
              name: '农业银行'
            }
            {
              name: '中国银行'
            }
            {
              name: '招商银行'
            }
            {
              name: '中信银行'
            }
            {
              name: '民生银行'
            }
            {
              name: '北京银行'
            }
            {
              name: '兴业银行'
            }
            {
              name: '交通银行'
            }
          ]
        }
        {
          name: '委托货币'
          values: [
            {
              name: '不限'
            }

            {
              name: '人民币'
              values:[
                currency: '人民币'
              ]
            }
            {
              name: '港币'
              values:[
                currency: '港币'
              ]
            }
            {
              name: '美元'
              values:[
                currency: '美元'
              ]
            }
            {
              name: '日元'
              values:[
                currency: '日元'
              ]
            }
            {
              name: '英镑'
              values:[
                currency: '英镑'
              ]
            }
            {
              name: '欧元'
              values:[
                currency: '欧元'
              ]
            }
            {
              name: '加拿大元'
              values:[
                currency: '加拿大元'
              ]
            }
            {
              name: '其他'
              values:[
                currency: '其他'
              ]
            }
          ]
        }
        {
          name: '产品期限'
          values:[
            {
              name: '不限'
              values: null
            }
            {
              name: '1个月内'
              values:[
                max_period: 1
              ]
            }
            {
              name: '1-3个月'
              values: [
                min_period: 1
                max_period: 3
              ]
            }
            {
              name: '3-6个月'
              values:[
                min_period: 3
                max_period: 6
              ]
            }
            {
              name: '6-12个月'
              values:[
                min_period: 6
                max_period: 12
              ]
            }
            {
              name: '1-2年'
              values: [
                min_period: 12
                max_period: 24
              ]
            }
            {
              name: '2年以上'
              values:[
                min_period: 24
              ]
            }
          ]
        }
        {
          name: '预期收益'
          values: [
            {
              name: '不限'
            }
            {
              name: '2.5%以下'
              values:[
                max_rate: 2.5
              ]
            }
            {
              name: '2.5%-4%'
              values:[
                min_rate: 2.5
                max_rate: 4
              ]
            }
            {
              name: '4%-5.5%'
              values:[
                min_rate: 4
                max_rate: 5.5
              ]
            }
            {
              name: '5.5%-7%'
              values:[
                min_rate: 5.5
                max_rate: 7
              ]
            }
            {
              name: '7%-10%'
              values:[
                min_rate: 7
                max_rate: 10
              ]
            }
            {
              name: '10%-15%'
              values:[
                min_rate: 10
                max_rate: 15
              ]
            }
            {
              name: '15%-20%'
              values:[
                min_rate: 15
                max_rate: 20
              ]
            }
            {
              name: '20%以上'
              values:[
                min_rate: 20
              ]
            }
          ]
        }
        {
          name: '收益类型'
          values: [
            {
              name: '不限'
            }
            {
              name: '保本固定收益'
              values:[
                profit_type: '保本固定收益'
              ]
            }
            {
              name: '保本浮动收益'
              values: [
                profit_type: '保本浮动收益'
              ]
            }
            {
              name: '非保本浮动收益'
              values:[
                profit_type: '非保本浮动收益'
              ]
            }
          ]
        }
      ]

      self.products = ko.observableArray [
      ]

      _.each self.filters, (value)->
        self.activeFilters.push value.values[0]



  model = new ViewModel()
  ko.applyBindings(model)