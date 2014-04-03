require.config(
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'
    'jquery.modal': 'lib/jquery.modal.min'
    purl: 'lib/purl'
    raphael: 'lib/raphael-min'
  shim:
    'jquery.modal': ['jquery']
    purl: ['jquery']
)

require ['jquery',
         'underscore',
         'knockout',
         'lib/backend',
         'lib/chart',
         'jquery.modal',
         'purl',
         'model/trustTable',
         'model/financingTable',
         'model/cashTable',
         'model/fundTable',
         'model/fund',
         'model/emptyTable'], ($, _, ko, backend, chart, modal, purl, trustTable, financingTable, cashTable, fundTable, fund, emptyTable)->
  class ViewModel

    constructor: ->
      self = this

      ###
      The user data: asset, risk, period
      ###
      asset_param = parseInt($.url(document.location.href).param('asset'))
      period_param = parseInt($.url(document.location.href).param('period'))
      risk_param = parseInt($.url(document.location.href).param('risk'))

      if isNaN(asset_param) or asset_param <= 0
        asset_param = 30
      if isNaN(period_param) or period_param <= 0
        period_param = 3
      if isNaN(risk_param) or risk_param <= 0
        risk_param = 1

      self.asset = ko.observable(asset_param)
      self.riskScore = ko.observable(risk_param)
      self.period = ko.observable(period_param)

      self.riskDescription = ko.observable()

      self.portfolioName = ko.observable()

      ko.computed ->
        risks =
          1: '完全不能承担任何风险'
          2: '可以承担极小的风险'
          3: '可以承担一定风险'
          4: '可以承担较大的风险来追求高收益'
          5: '绝对追求高收益'

        risk = self.riskScore()
        self.riskDescription risks[risk]

      self.finishSurvey = (data, event)->
        asset = self.questions[0].answer()
        if asset and parseInt(asset) > 0
          self.asset(parseInt(asset))

        period = self.questions[1].answer()
        if period and parseInt(period) > 0
          self.period(period)

        risk = self.questions[2].answer()
        if risk
          self.riskScore(risk.value.risk_score)

        $.modal.close()

      self.questions = [
        {
          question:'您的可投资资产是多少？'
          answer: ko.observable()
          input:
            suffix: '万元'
        }
        {
          question: '可以投资的期限是？'
          answer: ko.observable()
          input:
            suffix: '个月'
        }
        {
          question: '您的投资目标是？'
          answer: ko.observable()
          options:[
            {
              title: '不能承担任何风险'
              value:
                risk_score: 2
            }
            {
              title: '可承担一定的风险来换取较高的收益'
              value:
                risk_score: 3
            }
            {
              title: '可以承担很大的风险来追求高收益'
              value:
                risk_score: 4
            }
            {
              title: '绝对追求高收益'
              value:
                risk_score: 5
            }
          ]
        }
      ]

      ###
      The portfolio related stuff
      ###
      self.myPortfolio = ko.observable()
      self.productTypes = ko.observable()

      self.selectProduct = (value)->
        self.productsType value.productType
        self.amount(self.asset() * value.percent / 100)

      ko.computed ()->
        params =
          asset_min: self.asset()
          asset_max: self.asset()
          period_min: self.period()
          period_max: self.period()
          risk_score: self.riskScore()

        # TODO add error handling logic
        backend.loadPortfolio params
        .done (data)->
          self.myPortfolio(_.first data.results)
      .extend {throttle: 1}

      productTypeColorMapping =
        '现金': '#159629'
        '信托': '#7CB718'
        '银行理财': '#C3D40A'
        '货币基金': '#EC830A'
        '公募基金': '#E24809'
        'P2P': '#DE1F0E'
        '保险': '#BC0082'
      ko.computed ()->
        portfolio = self.myPortfolio()

        if portfolio?
          self.portfolioName portfolio.name

          self.productTypes(_.map portfolio.products, (value)->
            percent = value.value
            color = 'blue'
            if _.has productTypeColorMapping, value.product.name
              color = productTypeColorMapping[value.product.name]

            return {
              percent: percent
              color: color
              productType: value.product.name
            }
          )

          chart.PieChart( $('#portfolio')[0],
            x: 130
            y: 120
            r: 80
            pieces: self.productTypes()
            events:
              click: (data)->
                console.log 'set product type to' + data.productType
                self.productsType data.productType
                self.amount(self.asset() * data.percent / 100)
          )

      ###
      The filtered products related stuff
      ###
      self.trustTable = new trustTable.viewModel {
        fields:[
          '名称'
          '资金门槛'
          '产品期限'
          '预期收益'
          ''
        ]
      }
      self.financingTable = new financingTable.viewModel {
        fields:[
          '名称'
          '起购金额'
          '发行银行'
          '管理期限'
          '预期收益'
          ''
        ]
      }
      self.cashTable = new cashTable.viewModel {
        fields: [
          '名称'
          '发行机构'
          '期限'
          '七日年化利率'
          ''
        ]
      }
      self.fundTable = new fundTable.viewModel {
        fields: [
          '代码'
          '名称'
          '管理期限'
          '基金类型'
          '日涨幅'
          '近一月涨幅'
          ''
        ]
      }
      self.emptyTable = new emptyTable.viewModel {}
      self.dataTable = ko.observable()

      self.productsType = ko.observable()
      self.amount = ko.observable(0)

      ko.computed ()->
        type = self.productsType()
        amount = self.amount()
        if backend.isValidType type
          params =
            count: 7
            lte_threshold: amount

          backend.loadData type, params
          .done (data)->
            if data.results.length > 0
              normalizedType = backend.normalizeType(type)

              switch normalizedType
                when 'trusts'
                  self.trustTable.data data.results
                  self.dataTable self.trustTable
                when 'bank_financings'
                  self.financingTable.data data.results
                  self.dataTable self.financingTable
                when 'cashes'
                  self.cashTable.data data.results
                  self.dataTable self.cashTable
                when 'funds'
                  self.fundTable.data _.map(data.results, (item)->
                    new fund.viewModel
                      data: item
                  )

                  self.dataTable self.fundTable
                else
                  self.dataTable self.emptyTable
        else
          if console?
            console.log 'The type not supported'
          self.dataTable self.emptyTable

      .extend {throttle: 1}

  model = new ViewModel()
  ko.applyBindings model


