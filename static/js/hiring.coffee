require.config(
  paths:
    jquery: 'lib/jquery.min'
    underscore: 'lib/underscore-min'
    'jquery.modal': 'lib/jquery.modal.min'
  shim:
    'jquery.modal': ['jquery']
)

require ['jquery',
         'underscore',
         'lib/modal'], ($, _, modal)->
  $('a[data-role=modal]').click (e)->
    e.preventDefault()
    #autho: hetao; time: 2014.10.11; target: 修改招聘页弹框多了一个X的bug
    $(this).modal closeText: ''
