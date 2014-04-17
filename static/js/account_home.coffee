require.config(
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout'
)

require ['jquery', 'underscore', 'knockout',
         'lib/backend', 'lib/templateLoader',
         'model/portfolio', 'model/fund'], ($, _, ko, backend, templateLoader, portfolio, fund)->
  class DataViewModel
    constructor: ->
      self = this

      self.asset = ko.observable(300)
      self.riskScore = ko.observable(1)
      self.period = ko.observable(24)

      self.portfolio = ko.observable()

      ko.computed ()->
        params =
          lt_asset: self.asset()
          min_period: self.period()
          max_period: self.period()
          risk_score: self.riskScore()
        backend.loadPortfolio params
        .done (data)->
            self.portfolio new portfolio.viewModel
              data: data.results[0] #Just return the first matching portfolio for user TODO FIX THIS provide user's portfolio api and get the portfolio from there
              asset: self.asset
              events:
                productSelected: (value)->
                  type = value.product.name
                  self.productsType(type)

                  amount = value.value
                  if value.type == 'percent'
                    amount = amount / 100 * self.asset()
                  self.amount(amount)

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
          backend.loadData type, {
            count: 10
            max_threshold: amount
          }
          .done (data)->
            self.products = data.results
            #Hack to trigger the template_name change TODO Fix this
            if self.products.length > 0
              self.template_name(templateLoader.template type)
            else
              self.template_name('no-products-available')
        else
          # TODO add a way to notice user alegently
          if console?
            console.log 'The type not supported'
          self.products = null
          self.template_name('no-products-available')
      .extend {throttle: 1}

  viewModel = new DataViewModel()
  ko.applyBindings viewModel
