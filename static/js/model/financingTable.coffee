define ['jquery', 'underscore', 'model/table', 'model/financing'], ($, _, table, financing)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext =
        columns: [
            name: '序号'
            colspan: 1
            text: (item, index)->
              index + 1
          ,
            name: '名称'
            colspan: 3
            sortable: true
            field: 'short_name'
            text: (item)->
              '<a href="/financing/detail/' + item.id + '">' + item.short_name + '</a>'
          ,
            name: '状态'
            colspan: 1
            sortable: true
            field: 'status'
            text: (item)->
              item.status
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
              item.period + '天'
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
            name: '收藏'
            colspan: 1
            text: (item)->
              if item.is_favorited == 1
                '<a class="button button-mini button-white button-no-border" onclick="addToFavorite(event,' + "'financings');" +
                  '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">取消</a>'
              else
                '<a class="button button-mini button-white" onclick="addToFavorite(event,' + "'financings');" +
                  '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">收藏</a>'
          ,
            name: '详情'
            colspan: 1
            text: (item)->
              '<a class="button button-mini button-pink" href="/financing/detail/' + item.id + '">详情</a>'
          ]

      _.extend(context, defaultContext)
      super context

    transform_favorite: (products)->
      items = _.pluck(products.results, 'item')
      _.each items, (item)->
        item.is_favorited = 1
      @data _.map(items, (item)->
        new financing.viewModel
          data: item)

  viewModel: viewModel
