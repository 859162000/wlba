require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'
    purl: 'lib/purl'
  shim:
    'jquery.modal': ['jquery']
    purl: ['jquery']

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/pager', 'model/trustTable', 'purl', 'lib/filter'], ($, _, ko, backend, pager, table, purl, filter)->
  class DataViewModel
    constructor: ()->
      self = this

      self.trustTable = new table.viewModel
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

      self.hookExpandButton = (elements, data)->
        $('a[data-role=expand]').click (e)->
          e.preventDefault()

          parent = $(e.target).parent('.expandable')[0]
          maxHeight = '1000px'
          if $(parent).css('max-height') != maxHeight
            $(parent).css('max-height', maxHeight)
            $(e.target).text('收起')
          else
            $(parent).css('max-height', '')
            $(e.target).text('展开')

     # The filters
      self.filters = [
        {
          name: '资金门槛'
          param_name: 'asset'
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
              range: '0-50'
            }
            {
              name: '50-100万'
              values: [
                max_threshold: 100
                min_threshold: 50
              ]
              range: '50-100'
            }
            {
              name: '100-300万'
              values: [
                min_threshold: 100
                max_threshold: 300
              ]
              range: '100-300'
            }
            {
              name: '300万以上'
              values: [
                min_threshold: 300
              ]
              range: '>300'
            }
          ]
        }
        {
          name: '产品期限'
          param_name: 'period'
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
              range: '0-12'
            }
            {
              name: '12-36个月'
              values:[
                min_period: 12
                max_period: 36
              ]
              range: '12-36'
            }
            {
              name: '36个月以上'
              values: [
                min_period: 36
              ]
              range: '>36'
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
          expandable: true
          values: filter.arrayToFilter([
            '爱建信托','安信信托','百瑞信托','北方信托','北京国投','渤海信托','长安信托','长城新盛信托','大业信托','东莞信托','方正东亚信托','甘肃信托','国联信托','国民信托','国投信托','国元信托','杭州工商信托','华澳信托','华宝信托','华宸信托','华能贵诚','华融国际信托','华润信托','华信信托','华鑫信托','湖南信托','江苏信托','建信信托','交银国际信托','吉林信托','金谷信托','昆仑信托','陆家嘴信托','民生信托','平安信托','厦门信托','山东信托','上海信托','陕国投','山西信托','四川信托','苏州信托','天津信托','外贸信托','万向信托','五矿国际信托','西部信托','西藏信托','兴业国际信托','新华信托','新时代信托','英大信托','粤财信托','云国投','浙金信托','中诚信托','中海信托','中航信托','中江信托','中粮信托','重庆信托','中融信托','中泰信托','中铁信托','中投信托','中信信托','中原信托','紫金信托'
          ], 'issuer_name')
        }
      ]

      queries = $.url(window.location.href).param()

      _.each self.filters, (value)->
        if queries[value.param_name]
          _.every value.values, (item)->
            if backend.isInRange(queries[value.param_name], item['range'])
              self.activeFilters.push item
              return false
            else
              return true
        else
          self.activeFilters.push value.values[0]

      ko.computed ()->
        filters = _.chain(self.activeFilters()).pluck('values').flatten().compact().value()
        params = _(filters).reduce ((result, object)-> _.extend(result, object)),
          {
            page: self.pager.currentPageNumber()
            ordering: self.orderBy()
          }

        backend.loadData 'trusts', params
        .done( (data)->
          backend.joinFavorites(data, "trusts", self.trustTable)
          self.pager.totalPageNumber data.num_pages
        ).fail( (xhr, status, error)->
          alert(status + error)
        )
      .extend {throttle: 1}
  viewModel = new DataViewModel()
  ko.applyBindings viewModel
