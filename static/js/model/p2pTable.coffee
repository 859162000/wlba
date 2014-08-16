define ['jquery', 'underscore', 'model/table'], ($, _, table)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext =
        columns : [
            name: '名称'
            colspan: 3
            text: (item)->
              '<a target="_blank" class="blue" href="/p2p/detail/' + item.id + '">' + item.short_name + '</a>'
          ,
            name: '状态'
            colspan: 1
            sortable: true
            field: 'status'
            text: (item)->
              item.status
          ,
            name: '期限'
            colspan: 1
            sortable: true
            text: (item)->
              item.period + '个月'
            field: 'period'
          ,
            name: '预期收益'
            colspan: 2
            sortable: true
            text: (item)->
              item.expected_earning_rate.toFixed(2) + '%'
            field: 'expected_earning_rate'
          ]

      _.extend(context, defaultContext)
      super context

  viewModel: viewModel
