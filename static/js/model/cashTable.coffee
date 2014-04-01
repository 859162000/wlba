define ['jquery', 'underscore', 'model/table'], ($, _, table)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext = columns: [
        name: '序号'
        colspan: 1
        text: (item, index)->
          index + 1
      ,
        name: '名称'
        colspan: 3
        text: (item)->
          item.name
      ,
        name: '发行机构'
        colspan: 2
        sortable: true
        field: 'issuer__name'
        text: (item)->
          item.issuer_name
      ,
        name: '期限'
        colspan: 2
        sortable: true
        field: 'period'
        text: (item)->
          if item.period
            item.period + '个月'
          else
            '活期'
      ,
        name: '七日年化利率'
        colspan: 2
        sortable: true
        field: 'profit_rate_7days'
        text: (item)->
          item.profit_rate_7days + '%'
      ,
        name: '每万份收益'
        colspan: 2
        sortable: true
        field: 'profit_10000'
        text: (item)->
          item.profit_10000 + '元'
      ,
        name: '购买链接'
        colspan: 2
        text: (item)->
          '<a href="' + item.buy_url + '">' + item.buy_text + '</a>'
      ,
        name: ''
        colspan: 1
        text: (item)->
          link_text = '收藏'
          if item.is_favorited == 1
            link_text = '取消收藏'
          '<a class="button button-mini button-pink" onclick="addToFavorite(event,' + "'cashes');" +
            '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">' +
            link_text + '</a>'
      ,
        name: ''
        colspan: 1
        text: (item)->
          '<a class="button button-mini button-pink" href="/cash/detail/' + item.id + '">详情</a>'

      ]

      super _(defaultContext).extend context

    transform_favorite: (products)->
      items = _.pluck(products.results, 'item')
      _.each(items, (item)->
        item.is_favorited = 1)
      @data items


  viewModel: viewModel
