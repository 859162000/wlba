$(document).ready ->
  DataViewModel = ->
    self = this
    self.trusts = ko.observable []

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
      filter = $.param(value.filter);
      url = 'http://127.0.0.1:8000/api/trusts/.jsonp?&ordering=-issue_date&' + filter
      $.ajax(url, {
        dataType: 'jsonp'
      }).done( (data)->
        model.trusts data.results
      ).fail( (xhr, status, error)->
        alert(status + error)
      )
    return

  model = new DataViewModel()
  ko.applyBindings(model)
