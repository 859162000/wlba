require.config
  paths:
    jquery: 'lib/jquery.min'
    knockout: 'lib/knockout'
    underscore: 'lib/underscore-min'

require ['jquery', 'knockout', 'underscore', 'lib/backend', 'model/messageTable', 'model/pager',  'model/tab'], ($, ko, _, backend, message, pager, tab)->
#  class viewModel
#    constructor: ->
#      self = this
#
#      self.pager = new pager.viewModel()
#      self.pager.currentPageNumber(1)
#
#      self.messageTable = new message.viewModel {
#        fields:[
#          '类型'
#          '标题'
#          '时间'
#          '&nbsp;'
#        ]
#      }
#
#      self.tabTree =
#        tabs:[
#          name: '全部'
#          value: {
#            type: 'all'
#            table: self.messageTable
#          }
#        ,
#          name: '未读'
#          value: {
#            type: 'unread'
#            table: self.messageTable
#          }
#        ,
#          name: '已读'
#          value: {
#            type: 'read'
#            table: self.messageTable
#          }
#        ]
#
#      self.type = ko.observable()
#      self.dataTable = ko.observable()
#
#      self.tab = new tab.viewModel
#        tabs: self.tabTree.tabs
#        events:
#          tabSelected: (data, event)->
#            self.dataTable data.value.table
#            self.type data.value.type
#
#      ko.computed ()->
#        backend.loadMessage(self.type(),10,1)
#        .done (data)->
#          #self.dataTable().transform_message(data)
#          self.dataTable().isEmpty data.data.length == 0
#          num_pages = 0
#          backend.loadMessageCount(self.type())
#          .done (data)->
#            num_pages = (data.count)/10
#
#          self.pager.totalPageNumber num_pages
#
#  ko.applyBindings(new viewModel())

  $('.msg-id').click (e)->
    e.preventDefault()
    #console.log(e.currentTarget)
    msg_id = e.currentTarget.id
    msg_icon = $("#icon_" + msg_id).attr('class')
    read_status = $('#'+msg_id).attr('data-read-status')
    msg_id_id = $('#'+msg_id).attr('data-msg-id')
    if msg_icon == 'icon-msg-arrow-down'
      $("#cnt_" + msg_id).show()
      $("#title_" + msg_id).removeClass('blue')
      $("#icon_" + msg_id).removeClass('icon-msg-arrow-down')
      $("#icon_" + msg_id).addClass('icon-msg-arrow-up')

      if read_status == 'False'
        backend.readMessage(msg_id_id)
        .done (data)->
          $('#'+msg_id).attr('data-read-status','True')


    else
      $("#cnt_" + msg_id).hide()
      $("#icon_" + msg_id).removeClass('icon-msg-arrow-up')
      $("#icon_" + msg_id).addClass('icon-msg-arrow-down')

