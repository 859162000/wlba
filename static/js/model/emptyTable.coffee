define ['model/table'], (table)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext = columns: [
        name:'<p class="product-table-message">点击产品类别 查找符合条件的产品</p>'
        colspan: 1
      ]

      super _(defaultContext).extend context

  viewModel: viewModel