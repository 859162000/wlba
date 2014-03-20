require.config(
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'
    'jquery.modal': 'lib/jquery.modal.min'
    purl: 'lib/purl'
  shim:
    'jquery.modal': ['jquery']
    purl: ['jquery']
)

require ['jquery',
         'underscore',
         'knockout',
         'lib/backend',
         'jquery.modal',
         'purl',
         'model/portfolio',
         'model/trustTable',
         'model/financingTable',
         'model/cashTable',
         'model/fundTable',
         'model/fund',
         'model/emptyTable'], ($, _, ko, backend, modal, purl, portfolio, trustTable, financingTable, cashTable, fundTable, fund, emptyTable)->
  class ViewModel

    constructor: ->
      self = this

      ###
      The user data: asset, risk, period
      ###
      asset_param = parseInt($.url(document.location.href).param('asset'))
      if isNaN(asset_param) or asset_param <= 0
        asset_param = 30
      self.asset = ko.observable(asset_param)
      self.riskScore = ko.observable(null)
      self.period = ko.observable(6)

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
      self.portfolios = ko.observableArray []

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
          portfolios = _.map data.results, (data)->
            new portfolio.viewModel
              data: data
              asset: self.asset
              events:
                productSelected: (value, portfolio)->
                  for p in self.portfolios()
                    if p != portfolio
                      p.selectedProduct(null)
                  type = value.product.name
                  self.productsType(type)

                  amount = value.value
                  if value.type == 'percent'
                    amount = amount / 100 * self.asset()
                  self.amount(amount)

          self.portfolios(portfolios)
      .extend {throttle: 1}

      ###
      The filtered products related stuff
      ###
      self.trustTable = new trustTable.viewModel {}
      self.financingTable = new financingTable.viewModel {}
      self.cashTable = new cashTable.viewModel {}
      self.fundTable = new fundTable.viewModel {}
      self.emptyTable = new emptyTable.viewModel {}
      self.dataTable = ko.observable()

      self.productsType = ko.observable()
      self.amount = ko.observable(0)

      ko.computed ()->
        type = self.productsType()
        amount = self.amount()
        if backend.isValidType type
          params =
            count: 5
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
