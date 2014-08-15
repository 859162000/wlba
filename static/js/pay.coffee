require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.validate': 'lib/jquery.validate.min'
    'jquery.modal': 'lib/jquery.modal.min'
  shim:
    'jquery.validate': ['jquery']
)

require ['jquery', 'jquery.validate', 'lib/modal'], ($, validate, modal)->
  $('.banks a').click (e)->
    e.preventDefault()
    $('.banks a').removeClass 'active'
    $(e.target).addClass 'active'
    $('#gate_id').val $(e.target).attr('data-gate-id')
    $('.bank-description .bank-desc-container').hide()
    $('#' + $(e.target).attr('data-desc-id')).show()

  $('#pay').click (e)->
    e.preventDefault()
    if $('#id-is-valid').val() == 'False'
      $('#id-validate').modal()
      return
    if $(this).hasClass "disabled"
      return

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
      if parseFloat(value).toFixed(2) == "NaN"
        $(this).val ""
      else
        $(this).val parseFloat(value).toFixed(2)

  if $('#id-is-valid').val() == 'False'
    $('#id-validate').modal()
