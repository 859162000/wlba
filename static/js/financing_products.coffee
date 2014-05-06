require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout'
    purl: 'lib/purl'
  shim:
    'jquery.modal': ['jquery']
    purl: ['jquery']

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/financing', 'model/pager', 'model/financingTable', 'purl'], ($, _, ko, backend, financing, pager, table, purl)->
  class ViewModel
    constructor: ->
      self = this

      self.financingTable = new table.viewModel
        events:
          sortHandler: (column, order)->
            field = column.field
            if _.has(column, 'remote_field')
              field = column.remote_field
            if order != 'asc'
              field = '-' + column.field
            self.orderBy field

      self.orderBy = ko.observable('-status,-max_expected_profit_rate')

      ###
      Pager
      ###
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
        params = _(filters).reduce ((result, object)-> _.extend(result, object)),
          {
            page: self.pager.currentPageNumber()
            ordering: self.orderBy()
          }

        backend.loadData 'financing', params
        .done( (data)->
          backend.joinFavorites(data, 'financings', self.financingTable)
          self.pager.totalPageNumber data.num_pages
        ).fail( (xhr, status, error)->
          alert(status + error)
        )

      arrayToFilter = (names, field)->
        filters = _.map names, (val, index)->
          {
            name: val
            values:
              _.object([[field, val]])
          }
        [{
          name:'不限'
        }].concat filters

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

      self.filters = [
        {
          name : '销售状态'
          values: arrayToFilter([
            '在售'
            '预售'
            '停售'
          ], 'status')
        }
        {
          name : '发行银行'
          expandable: true
          values: arrayToFilter([
            '包商银行'
            '中国银行'
            '招商银行'
            '平安银行'
            '广发银行'
            '交通银行'
            '南京银行'
            '农业银行'
            '建设银行'
            '杭州银行'
            '工商银行'
            '兴业银行'
            '光大银行'
            '天津银行'
            '浦东发展银行'
            '华夏银行'
            '北京银行'
            '上海银行'
            '河北银行'
            '中信银行'
            '宁波银行'
            '徽商银行'
            '广州银行'
            '威海市商业银行'
            '中国邮政储蓄银行'
            '浙江稠州商行'
            '汉口银行'
            '南洋商业银行'
            '渤海银行'
            '广东华兴银行'
            '青岛银行'
            '昆山农村商业银行'
            '无锡农商行'
            '天津农商行'
            '哈尔滨银行'
            '晋商银行'
            '北京农商行'
            '顺德农村商业银行'
            '德阳银行'
            '绍兴银行'
            '重庆银行'
            '苏州银行'
            '汇丰银行'
            '齐鲁银行'
            '浙商银行'
            '上饶银行'
            '南海农商银行'
            '兰州银行'
            '重庆三峡银行'
            '厦门银行'
            '锦州银行'
            '成都农商行'
            '浙江泰隆商业银行'
            '广州农商银行'
            '泉州银行'
            '上海农商行'
            '黄河农商行'
            '富滇银行'
            '成都银行'
            '南昌银行'
            '重庆农村商业银行'
            '辽阳银行'
            '淮海农商行'
            '泰安市商业银行'
            '东莞银行'
            '龙江银行'
            '湖北银行'
            '大连银行'
            '宁夏银行'
            '盛京银行'
            '邳州农商行'
            '东亚银行'
            '太仓农村商业银行'
            '大华银行(中国)'
            ], 'bank_name')
        }
        {
          name: '委托货币'
          values: arrayToFilter([
            '人民币'
            '港币'
            '美元'
            '日元'
            '英镑'
            '欧元'
            '加拿大元'
            '其他'
          ], 'currency')
        }
        {
          name: '产品期限'
          param_name: 'period'
          values:[
            {
              name: '不限'
            }
            {
              name: '3个月以内'
              values:
                gte_period: 30
                lt_period: 90
              range: '0-3'
            }
            {
              name: '3-6个月'
              values:
                gte_period: 90
                lt_period: 180
              range: '3-6'
            }
            {
              name: '6-12个月'
              values:
                gte_period: 180
                lt_period: 365
              range: '6-12'
            }
            {
              name: '1年以上'
              values:
                gte_period: 365
              range: '>12'
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
              values:
                max_rate: 2.5
            }
            {
              name: '2.5%-4%'
              values:
                min_rate: 2.5
                max_rate: 4
            }
            {
              name: '4%-5.5%'
              values:
                min_rate: 4
                max_rate: 5.5
            }
            {
              name: '5.5%-7%'
              values:
                min_rate: 5.5
                max_rate: 7
            }
            {
              name: '7%以上'
              values:
                min_rate: 7
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
              values:
                profit_type: '保本固定收益型'
            }
            {
              name: '保本浮动收益'
              values:
                profit_type: '保本浮动收益型'
            }
            {
              name: '非保本浮动收益'
              values:
                profit_type: '非保本浮动收益型'
            }
          ]
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
          self. activeFilters.push value.values[0]

      ko.computed ()->
        self.queryData()
      .extend {throttle: 1}

  model = new ViewModel()
  ko.applyBindings(model)