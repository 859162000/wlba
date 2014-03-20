define ['model/table'], (table)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext = columns: [
        name:'点击产品类别 查找符合条件的产品'
        colspan: 1
      ]

      super _(defaultContext).extend context

  viewModel: viewModel