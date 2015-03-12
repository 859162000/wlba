define ['jquery', 'underscore', 'model/table'], ($, _, table)->
  class viewModel extends table.viewModel
    constructor: (context)->
      defaultContext =
        columns : [
            name: '类型'
            colspan: 1
            text: (item)->
              item.mtype
          ,
            name: '标题'
            colspan: 1
            text: (item)->
                '<p class="blue" data-id="' + item.id + '">'+ item.title +'</p>' +
                '<p class="message-content">'+ item.content +'</p>'
          ,
            name: '时间'
            colspan: 1
            text: (item)->
              item.created_at
          ,
            name: '&nbsp;'
            colspan: 1
            text: (item)->
              '<span class="icon icon-msg-arrow-down" id="'+ item.id +'"></span>'
          ]

      _.extend(context, defaultContext)
      super context

      transform_message: (msg)->
        items = _.pluck(msg.data, 'item')
        _.each(items, (item)->
          item.is_read = 1)
        @data items

  viewModel: viewModel
