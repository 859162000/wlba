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
         'model/portfolio', 'tools',
         'lib/modal'], ($, _, ko, backend, templateLoader, portfolio, tool, modal)->

  $('.more_btn').click () ->
    $('.tableNew').slideToggle()

  $('#showMark').click () ->
    $('.explain_box').modal()
    $('.modal').removeClass('modal')
    $('.explain_box').css('margin-left':'-435px')

  $('.investBtn').click () ->
    $.ajax {
      url: '/api/experience/buy/'
      type: "POST",
      data: {}
    }
    .done (data) ->
      $('#success').modal()
      $('#success').find('.close-modal').hide()
      setInterval( ->
        $.modal.close()
        location.reload()
      ,2000)
    .fail (data)->
      console.log(1111)


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

  $(".xunlei-binding-modal").click () ->
    $('#xunlei-binding-modal').modal()

  isXunleiBindSuccess = () ->
    result = backend.getRequest()

    if result['ret'] && result['ret'] > 0
      tool.modalAlert({title: '温馨提示', msg: '迅雷帐号绑定失败'})

    if !result['ret'] || !result['code'] || !result['state']
      return
    backend.registerXunlei {
      "ret":result['ret'],
      "code":result['code'],
      "state":result['state']
    }
    .done (data)->
      if data.ret_code == 0
        if data.isvip == 0
          tool.modalAlert({title: '温馨提示', msg: '抱歉您还不是迅雷付费会员，不能享受额外收益。<br/>请开通迅雷付费会员后，再绑定一次，即可享受额外收益。', callback_ok: ()->
            window.location.href = "/accounts/home/"
          })
        else
          tool.modalAlert({title: '温馨提示', msg: '恭喜！迅雷付费会员绑定成功，投资指定标的后可享受额外收益。', callback_ok: ()->
            window.location.href = "/accounts/home/"
          })
      else if data.ret_code == 30035
        tool.modalAlert({title: '温馨提示', msg: '绑定失败。你使用的迅雷帐号已被绑定，请换一个帐号再试。', callback_ok: ()->
            window.location.href = "/accounts/home/"
          })
      else
        tool.modalAlert({title: '温馨提示', msg: '迅雷帐号绑定失败，请再试一次'})


  isXunleiBindSuccess()

