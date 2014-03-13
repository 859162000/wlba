require.config
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    knockout: 'lib/knockout-3.0.0'

require ['jquery', 'underscore', 'knockout', 'lib/backend', 'model/cash'], ($, _, ko, backend, cash)->
  $ document
  .ready ->
    class DataViewModel
      constructor: ->
        self = this

        self.products = ko.observable()

        ko.computed ()->
          params = {count:10}

          backend.loadData 'cashes', params
          .done (data)->
            self.products _.map(data.results, (item)->
              new cash.viewModel
                data: item
            )
        .extend {throttle: 1}

    viewModel = new DataViewModel()
    ko.applyBindings viewModel