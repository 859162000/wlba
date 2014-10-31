require.config(
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout'
    tools: 'lib/modal.tools'
    'jquery.modal': 'lib/jquery.modal.min'
)

require ['jquery', 'underscore', 'knockout',
         'lib/backend', 'lib/templateLoader',
         'model/portfolio', 'tools', 'lib/jquery.number.min',
         'lib/modal'], ($, _, ko, backend, templateLoader, portfolio, tool, modal)->
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

  backend.fundInfo()
  .done (data)->
    totalAsset = parseFloat($("#total_asset").attr("data-p2p")) + parseFloat(data["fund_total_asset"])
    $("#total_asset").text($.number(totalAsset, 2))
    $("#fund_total_asset").text($.number(data["fund_total_asset"], 2))
    $("#fund_total_asset_title").text($.number(data["fund_total_asset"], 2))
    $("#total_income").text($.number(data["total_income"], 2))
    $("#fund_income_week").text($.number(data["fund_income_week"], 2))
    $("#fund_income_month").text($.number(data["fund_income_month"], 2))
    return
  .fail (data)->
    tool.modalAlert({title: '温馨提示', msg: '基金获取失败，请刷新重试！', callback_ok: ()->
              location.reload()
          })
    return

  $(".xunlei-binding-modal").click () ->
    $('#xunlei-binding-modal').modal()
