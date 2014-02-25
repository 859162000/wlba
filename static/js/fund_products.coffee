require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', ''], ($, _, ko)->
  class viewModel
    constructor: ()->
      self = this

      self.products = ko.observable()

    # TODO finish this this is not finished, the whole page for fund_products is just a placeholder

  ko.applyBindings new viewModel()