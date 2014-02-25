require.config
  paths:
    jquery: 'lib/jquery.min'
    knockout: 'lib/knockout-3.0.0'
    underscore: 'lib/underscore-min'

require ['jquery', 'underscore', 'knockout', 'lib/backend'], ($, _, ko, backend)->
  $(document).ready ->
    class DataViewModel
      constructor: ->
        self = this
        self.trusts = ko.observable []
        self.latestTrusts = ko.observable []

        self.tabTree = [
          {
            name: '按期限'
            values:[
              {
                name: '12个月以内'
                filter:
                  max_period: 12
              }
              {
                name: '12个月-24个月'
                filter:
                  min_period: 12
                  max_period: 24
              }
              {
                name: '24个月以上'
                filter:
                  min_period: 24
              }
            ]
          }
          {
            name: '按起点'
            values: [
              {
                name: '100万以下'
                filter:
                  'max_threshold': 100.0
              }
              {
                name: '100万-300万'
                filter:
                  min_threshold: 100.0
                  max_threshold: 300.0
              }
              {
                name: '300万以上'
                filter:
                  min_threshold: 300
              }
            ]
          }
          {
            name: '按收益'
            values:[
              {
                name: '13%以上'
                filter:
                  min_rate: 13
              }
              {
                name: '10%-13%'
                filter:
                  min_rate: 10
                  max_rate: 13
              }
              {
                name: '低于10%'
                filter:
                  max_rate: 10
              }
            ]
          }
        ]

        self.selectedTab = ko.observable(self.tabTree[0])
        self.selectedValue = ko.observable(self.selectedTab().values[0])

        self.setSelectedTab = (tab)->
          self.selectedTab(tab)

        self.setSelectedValue = (value)->
          self.selectedValue(value)

          params = _.extend
            ordering: '-issue_date'
            count: 10
            , value.filter

          backend.loadData('trust', params).done( (data)->
            model.trusts data.results
          ).fail( (xhr, status, error)->
            alert(status + error)
          )

    model = new DataViewModel()
    ko.applyBindings(model)

    backend.loadData 'trust',
      count: 10
      ordering: '-issue_date'
    .done (data)->
        model.latestTrusts(data.results)
