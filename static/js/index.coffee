require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', 'lib/backend'], ($, _, ko, backend)->
  $(document).ready ->
    class DataViewModel
      constructor: ()->
        self = this

        self.trusts = ko.observable (_.pluck data.hot_trusts, 'trust')
        self.funds = ko.observable (_.pluck data.hot_funds, 'fund')
        self.financings = ko.observable (_.pluck data.hot_financings, 'bank_financing')

    model = new DataViewModel()
    ko.applyBindings(model)
