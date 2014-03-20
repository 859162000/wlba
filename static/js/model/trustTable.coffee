define ['jquery', 'underscore', 'model/table'], ($, _, table)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext =
        columns : [
            name: '序号'
            colspan: 1
            text: (item, index)->
              index + 1
          ,
            name: '名称'
            colspan: 4
            text: (item)->
              item.name
          ,
            name: '资金门槛'
            colspan: 2
            sortable: true
            text: (item)->
              item.investment_threshold + '万'
            field: 'investment_threshold'
          ,
            name: '产品期限'
            colspan: 2
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
          ,
            name: '投资行业'
            colspan: 2
            sortable: true
            text: (item)->
              item.usage
            field: 'usage'
          ,
            name: '信托分类'
            colspan: 2
            sortable: true
            text: (item)->
              item.type
            field: 'type'
          ,
            name: '信托公司'
            colspan: 2
            sortable: true
            text: (item)->
              item.issuer_short_name
            remote_field: 'issuer__short_name'
            field: 'issuer_short_name'
          ,
            name: ''
            colspan: 3
            text: (item)->
              link_text = '收 藏'
              if item.is_favorited == 1
                link_text = '取消收藏'
              '<a class="button button-mini button-yellow" href="/trust/detail/' + item.id + '">详情</a>' +
                ' <a class="button button-mini button-yellow" onclick="addToFavorite(event);" href="#" data-is-favorited=' +
                  item.is_favorited + ' data-id="' + item.id + '">' + link_text + '</a>'
          ]


      _.extend(context, defaultContext)
      super context

  viewModel: viewModel
