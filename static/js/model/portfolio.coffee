define ['knockout', 'underscore'], (ko, _)->
  class viewModel

    titleWidthPercent: 10

    constructor: (context)->
      self = this

      data = context.data

      self.name = ko.observable data.name
      self.products = ko.observableArray data.products

      if context and _.has(context, 'asset')
        self.asset = context.asset
      else
        self.asset = ko.observable 100

      self.events = {}
      if _.has(context, 'events')
        self.events = _.extend(self.events, context.events)

      self.productSelected = (product)->
        if _.has(self.events, 'productSelected')
          self.events.productSelected(product)
        else
          if console?
            console.log product

    data: (data)->
      this.name(data.name)
      this.products(data.products)

    productDescription: (productEntry)->
      percent = 0
      amount = 0
      asset = this.asset()
      if productEntry.type == 'percent'
        percent = productEntry.value
        amount = percent / 100 * asset
      else
        amount = productEntry.value
        percent = amount / asset * 100

      return amount.toFixed(0) + '万 ' + percent.toFixed(0) + '%'

    productWidth: (productEntry)->
      (100 - this.titleWidthPercent) / this.products().length + '%'

  viewModel: viewModel
