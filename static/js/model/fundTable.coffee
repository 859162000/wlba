define ['jquery', 'underscore', 'model/table'], ($, _, table)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext =
        columns: [
          name: '代码'
          colspan: 2
          field: 'product_code'
          text: (item)->
            item.product_code
        ,
          name: '基金名称'
          colspan: 3
          sortable: true
          field: 'name'
          text: (item)->item.name
        ,
          name: '基金类型'
          colspan: 2
          sortable: true
          field: 'type'
          text: (item)->item.type
        ,
          name: '单位净值'
          colspan: 2
          sortable: true
          field: 'face_value'
          text: (item)->item.face_value
        ,
          name: '日涨幅'
          colspan: 2
          sortable: true
          field: 'rate_day'
          text: (item)->item.rate_day + '%'
        ,
          name: '近一月涨幅'
          colspan: 2
          sortable: true
          field: 'profit_rate_month'
          text: (item)->item.profit_rate_month + '%'
        ,
          name: '近三月涨幅'
          colspan: 2
          sortable: true
          field: 'profit_rate_3months'
          text: (item)->item.profit_rate_3months + '%'
        ,
          name: '近半年涨幅'
          colspan: 2
          sortable: true
          field: 'profit_rate_6months'
          text: (item)->item.profit_rate_6months + '%'
        ,
          name: '前端|后端费率'
          colspan: 2
          text: (item)->
            item.frontEndRate() + '|' + item.backEndRate()
        ,
          name: ''
          colspan: 2
          text: (item)->
            link_text = '收 藏'
            if item.is_favorited == 1
              link_text = '取消收藏'
            '<a class="button button-mini button-yellow" href="/fund/detail/' + item.id + '">详情</a>' +
              ' <a class="button button-mini button-yellow" onclick="addToFavorite(event,' + "'funds');" +
              '" href="#" data-is-favorited=' + item.is_favorited + ' data-id="' + item.id + '">' +
              link_text + '</a>'
      ]

      _.extend(context, defaultContext)
      super context

  viewModel: viewModel
