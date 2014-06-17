require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.validate': 'lib/jquery.validate.min'
  shim:
    'jquery.validate': ['jquery']
)

require ['jquery', 'jquery.validate'], ($, validate)->
  $('.banks a').click (e)->
    e.preventDefault()

    $('.banks a').removeClass 'active'
    $(e.target).addClass 'active'
    $('#gate_id').val $(e.target).attr('data-gate-id')
    $('.bank-description .bank-desc-container').hide()
    $('#' + $(e.target).attr('data-desc-id')).show()

  $("#payform").validate
    rules:
      amount:
        required: true
      gate_id:
        required: true

    messages:
      amount:
        required: '不能为空'

  $("#amount").blur ->
    value = $(this).val()
    if value
      $(this).val parseFloat(value).toFixed(2)
