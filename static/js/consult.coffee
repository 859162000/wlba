require.config(
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout'
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
         'lib/modal',
         'purl',
         'model/trustTable',
         'model/fundTable',
         'model/fund',
         'model/emptyTable'], ($, _, ko, backend, chart, modal, purl, trustTable, fundTable, fund, emptyTable)->

  class ViewModel
    constructor: (asset_param, period_param)->
      self = this
      self.asset = ko.observable(asset_param)
      self.period = ko.observable(period_param)

      self.portfolioName = ko.observable()
      self.portfolioEarningRate = ko.observable(0)
      self.bankRate = .35
      self.timesBankRate = ko.observable(1)

      self.finishSurvey = (data, event)->
        asset = self.questions[0].answer()
        if asset and parseInt(asset) > 0
          self.asset(parseInt(asset))

        period = self.questions[1].answer()
        if period and parseInt(period) > 0
          self.period(period)

        $.modal.close()

      self.questions = [
        {
          question:'投资金额'
          answer: ko.observable(self.asset())
          input:
            suffix: '万元'
        }
        {
          question: '投资期限'
          answer: ko.observable(self.period())
          input:
            suffix: '个月'
        }
      ]

      self.savePortfolio = ->
        backend.userProfile
          investment_asset: self.asset()
          investment_period: self.period()
        .done ->
          alert '投资方案已保存！预约理财热线：400-8588-066。'
        .fail (jqXHR, textStatus, errorThrown)->
          if jqXHR.status == 403
            window.location.href = '/accounts/register/?next=' + window.location.href
          else
            alert '保存投资方案失败'

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
          self.productsType portfolio.products[0].product.name

          rate = 0
          self.productTypes(_.map portfolio.products, (value)->
            percent = value.value
            color = '#159629'
            if _.has productTypeColorMapping, value.product.name
              color = productTypeColorMapping[value.product.name]

            rate += value.product.average_earning_rate * percent / 100

            return {
              percent: percent
              color: color
              productType: value.product.name
              earning_rate: value.product.average_earning_rate
            }
          )
          self.portfolioEarningRate rate
          self.timesBankRate Math.round(rate / self.bankRate)

          chart.PieChart( $('#portfolio')[0],
            x: 130
            y: 120
            r: 80
            pieces: self.productTypes()
            events:
              click: (data)->
                self.productsType data.productType
                self.amount(self.asset() * data.percent / 100)
          )

      ###
      The filtered products related stuff
      ###
      self.trustTable = new trustTable.viewModel {
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
      self.fundTable = new fundTable.viewModel {
        fields: [
          '名称'
          '七日年化利率'
          '近一月收益率'
          '起购金额(元)'
          '购买'
          '收藏'
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
                  backend.joinFavorites(data, "trusts", self.trustTable)
                  self.dataTable self.trustTable
                when 'funds'
                  backend.joinFavorites(data, 'funds', self.fundTable, (data)->
                    return _.map(data.results, (item)->
                        new fund.viewModel
                          data: item))

                  self.dataTable self.fundTable
                else
                  self.dataTable self.emptyTable
        else
          if console?
            console.log 'The type not supported'
          self.dataTable self.emptyTable

      .extend {throttle: 1}

  if not $.url(document.location.href).param('asset')
    backend.userProfile()
    .done (data)->
      asset_param = data.investment_asset
      period_param = data.investment_period
      model = new ViewModel(asset_param, period_param)
      ko.applyBindings model
    .fail ->
      model = new ViewModel(30, 3, 1)
      ko.applyBindings model
  else
    asset_param = parseInt($.url(document.location.href).param('asset'))
    period_param = parseInt($.url(document.location.href).param('period'))

    if isNaN(asset_param) or asset_param <= 0
      asset_param = 30

    if isNaN(period_param) or period_param <= 0
      period_param = 3

    model = new ViewModel(asset_param, period_param)
    ko.applyBindings model

  $('#question-button').click (e)->
    e.preventDefault()
    $(this).modal()

