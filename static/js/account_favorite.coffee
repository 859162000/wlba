require.config
  paths:
    jquery: 'lib/jquery.min'
    knockout: 'lib/knockout'
    underscore: 'lib/underscore-min'

require ['jquery', 'knockout', 'underscore', 'lib/backend', 'model/fundTable', 'model/financingTable', 'model/trustTable', 'model/cashTable', 'model/tab'], ($, ko, _, backend, fund, financing, trust, cash, tab)->
  class viewModel
    constructor: ->
      self = this

      self.trustTable = new trust.viewModel {
        fields:[
          '名称'
          '状态'
          '资金门槛'
          '产品期限'
          '预期收益'
          '收藏'
          '详情'
        ]
      }
      self.financingTable = new financing.viewModel {
        fields:[
          '名称'
          '起购金额'
          '管理期限'
          '预期收益'
          '收藏'
          '详情'
        ]
      }
      self.cashTable = new cash.viewModel {
        fields: [
          '名称'
          '发行机构'
          '期限'
          '七日年化利率'
          '收藏'
          '详情'
        ]
      }
      self.fundTable = new fund.viewModel {
        fields: [
          '名称'
          '管理期限'
          '基金类型'
          '近一月涨幅'
          '近三月涨幅'
          '收藏'
          '详情'
        ]
      }

      self.tabTree =
        tabs:[
          name: '信托'
          value: {
            type: 'trusts'
            table: self.trustTable
          }
        ,
          name: '银行理财'
          value: {
            type: 'financings'
            table: self.financingTable
          }
        ,
          name: '基金'
          value: {
            type: 'funds'
            table: self.fundTable
          }
        ,
          name: '现金类理财'
          value: {
            type: 'cashes'
            table: self.cashTable
          }
        ]

      self.type = ko.observable()
      self.dataTable = ko.observable()

      self.tab = new tab.viewModel
        tabs: self.tabTree.tabs
        events:
          tabSelected: (data, event)->
            self.dataTable data.value.table
            self.type data.value.type

      ko.computed ()->
        backend.loadFavorites(self.type())
        .done (data)->
            self.dataTable().transform_favorite(data)
            self.dataTable().isEmpty data.results.length == 0

  ko.applyBindings(new viewModel())
