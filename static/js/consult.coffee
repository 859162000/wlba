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

require ['jquery', 'underscore', 'knockout', 'lib/backend',  'lib/templateLoader', 'jquery.modal', 'purl', 'model/portfolio'], ($, _, ko, backend, templateLoader, modal, purl, portfolio)->
  $ document
  .ready ->
    class ViewModel

      constructor: ->
        self = this

        ###
        The user data: asset, risk, period
        ###
        asset_param = parseInt($.url(document.location.href).param('asset'))
        if not asset_param or asset_param <= 0
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
                  productSelected: (value)->
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
        self.products = null
        self.productsType = ko.observable()
        self.template_name = ko.observable()
        self.amount = ko.observable(0)

        ko.computed ()->
          type = self.productsType()
          amount = self.amount()
          if backend.isValidType type
            params =
              count: 10
              lte_threshold: amount

            backend.loadData type, params
            .done (data)->
              self.products = data.results
              #Hack to trigger the template_name change TODO Fix this
              if self.products.length > 0
                self.template_name('')
                self.template_name(templateLoader.template type)
              else
                self.template_name('no-products-available')
          else
            # TODO add a way to notice user alegently
            console.log 'The type not supported'
            self.products = null
            self.template_name('no-products-available')

        .extend {throttle: 1}

    model = new ViewModel()
    ko.applyBindings model
