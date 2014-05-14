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
  $(document).ready ->
    $('a[data-role=modal]').click (e)->
      e.preventDefault()
      $(this).modal()
