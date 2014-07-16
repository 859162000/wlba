require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.ui': 'lib/jquery-ui.min'

  shim:
    'jquery.ui': ['jquery']
)

require ['jquery', 'jquery.ui'], ($, jqueryui)->
  $("#datepicker").datepicker()
