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

        self.trusts = ko.observable []

    model = new DataViewModel()
    ko.applyBindings(model)

    backend.loadData 'trusts',
      count: 6
      ordering: '-issue_date'
    .done (data) ->
      model.trusts data.results
    .fail (xhr, status, error) ->
      alert(status + error)