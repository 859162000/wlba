$ document
.ready ->

  class ViewModel

    constructor: ->
      self = this

      ###
      The user data: asset, risk, period, preference
      ###
      self.asset = ko.observable(30)
      self.riskScore = ko.observable(2)
      self.period = ko.observable(6)
      self.preference = ko.observable(null)

      self.finishSurvey = (data, event)->
        asset = self.questions[0].answer()
        if asset != null and parseInt(asset) > 0
          self.asset(parseInt(asset))

        period = self.questions[1].answer()
        if period != null and parseInt(period) > 0
          self.period(period)

        risk = self.questions[2].answer()
        if risk != null
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
      self.titleWidthPercent = 10
      self.portfolios = ko.observableArray []

      ko.computed ()->
        params =
          asset_min: self.asset()
          asset_max: self.asset()
          period_min: self.period()
          period_max: self.period()
          risk_score: self.riskScore()
          investment_preference: self.preference()

        url = 'http://127.0.0.1:8000/api/portfolios/.jsonp?' + $.param(params)

        # TODO add error handling logic
        $.ajax(url, {
          dataType: 'jsonp'
        }).done (data)->
          self.portfolios(data.results)
      .extend {throttle: 1}

      self.productDescription = (productEntry)->
        percent = 0
        amount = 0
        if productEntry.type == 'percent'
          percent = productEntry.value
          amount = percent / 100 * self.asset()
        else
          amount = productEntry.value
          percent = amount / self.asset() * 100

        return amount.toFixed(0) + '万 ' + percent.toFixed(0) + '%'

      self.productWidth = (productEntry, portfolio)->
        (100 - self.titleWidthPercent)/portfolio.products.length + '%'


      ###
      The filtered products related stuff
      ###
      self.products = null
      self.productsType = ko.observable('trusts')
      self.template_name = ko.observable('trust-table')
      self.amount = ko.observable(0)

      self.setSelectedProduct = (value, event)->
        amount = value.value
        if value.type == 'percent'
          amount = amount / 100 * self.asset()
        self.amount(amount)

        productTypeName = value.product.name
        if productTypeName == '信托'
          self.productsType('trusts')
        else if productTypeName == '银行理财'
          self.productsType('bank_financings')
        else
          self.productsType(null)

      self.productMapping =
        trusts:
          template: 'trust-table'
        bank_financings:
          template: 'financing-table'

      ko.computed ()->
        type = self.productsType()
        amount = self.amount()
        if type
          url = 'http://127.0.0.1:8000/api/' + type + '/.jsonp?count=10&max_threshold=' + amount
          $.ajax(url, {
            dataType:'jsonp'
          }).done( (data)->
            self.products = data.results
            #Hack to trigger the template_name change TODO Fix this
            if self.products.length > 0
              self.template_name('')
              self.template_name(self.productMapping[type].template)
            else
              self.template_name('no-products-available')
          )
        else
          # TODO add a way to notice user alegently
          console.log 'The type not supported'
      .extend {throttle: 1}



  model = new ViewModel()
  ko.applyBindings model
