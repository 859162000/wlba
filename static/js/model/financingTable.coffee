define ['jquery', 'underscore', 'model/table'], ($, _, table)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext =
        columns: [
            name: '序号'
            colspan: 1
            text: (item, index)->
              index + 1
          ,
            name: '产品名称'
            colspan: 4
            sortable: true
            field: 'name'
            text: (item)->
              item.name
          ,
            name: '起购金额'
            colspan: 2
            sortable: true
            field: 'investment_threshold'
            text: (item)->
              item.investment_threshold + '万'
          ,
            name: '发行银行'
            colspan: 2
            sortable: true
            text: (item)->
              item.bank_name
            field: 'bank_name'
            remote_field: 'bank__name'
          ,
            name: '管理期限'
            colspan: 2
            sortable: true
            text: (item)->
              item.period + '个月'
            field: 'period'
          ,
            name: '收益类型'
            colspan: 2
            sortable: true
            text: (item)->
              item.profit_type
            field: 'profit_type'
          ,
            name: '预期收益'
            colspan: 2
            sortable: true
            text: (item)->
              item.expected_rate + '%'
            field: 'expected_rate'
          ,
            name: ''
            colspan: 2
            text: (item)->
              '<a class="button button-mini button-yellow" href="/financing/detail/' + item.id + '">详情</a>'
          ]

      _.extend(context, defaultContext)
      super context

  viewModel: viewModel
