define ['jquery', 'underscore', 'model/table', 'model/fund'], ($, _, table, fund)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext =
        columns: [
          name: '代码'
          colspan: 2
          field: 'product_code'
          text: (item)->item.product_code
        ,
          name: '名称'
          colspan: 3
          sortable: true
          field: 'name'
          text: (item)->
            '<a class="blue" target="_blank" href="/fund/detail/' + item.id + '">' + item.name + '</a>'
        ,
          name: '七日年化利率'
          colspan: 2
          sortable: true
          field: 'rate_7_days'
          text: (item)->item.rate_7_days+ '%'
        ,
          name: '近一月涨幅'
          colspan: 2
          sortable: true
          field: 'rate_1_month'
          text: (item)->item.rate_1_month + '%'
        ,
          name: '近三月涨幅'
          colspan: 2
          sortable: true
          field: 'rate_3_months'
          text: (item)->item.rate_3_months + '%'
        ,
          name: '起购金额(元)'
          colspan: 2
          sortable: true
          field: 'investment_threshold'
          text: (item)->item.investment_threshold
        ,
          name: '购买'
          colspan: 1
          text: (item)->
            if item.availablefund
              '<a class="button button-mini button-pink" href="/shumi/oauth/check_oauth_status/?fund_code=' + item.product_code + '&action=purchase" target="_blank"> 购买 </a>'
            else
              '<a class="button button-mini button-gray" href="javascript:void(0)"> 购买 </a>'
        ,
          name: '收藏'
          colspan: 1
          text: (item)->
            if item.is_favorited == 1
              '<a class="button button-mini button-white button-no-border" onclick="addToFavorite(event,' + "'funds');" +
                '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">取消</a>'
            else
              '<a class="button button-mini button-white" onclick="addToFavorite(event,' + "'funds');" +
                '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">收藏</a>'

      ]

      _.extend(context, defaultContext)
      super context


    transform_favorite: (products)->
      items = _.pluck(products.results, 'item')
      _.each(items, (item)->
        item.is_favorited = 1)
      @data _.map(items, (item)->
                  new fund.viewModel
                    data: item)

  viewModel: viewModel
