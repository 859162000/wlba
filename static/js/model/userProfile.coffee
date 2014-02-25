define [], ()->
  class viewModel
    constructor: (context)->
      self = this

      self.name = ko.observable()
      self.phone = ko.observable() # It is not a good idea to have phone number showed, the server may return a stripped version like 138xxxx2222

      self.asset = ko.observable()
      self.riskScore = ko.observable()
      self.period = ko.observable()


  viewModel: viewModel
