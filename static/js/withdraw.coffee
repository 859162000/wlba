require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.placeholder': 'lib/jquery.placeholder'
    'jquery.validate': 'lib/jquery.validate.min'

  shim:
    'jquery.modal': ['jquery']
    'jquery.placeholder': ['jquery']
    'jquery.validate': ['jquery']
)

require ['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder', 'lib/calculator', 'jquery.validate'], ($, modal, backend, placeholder, validate)->

  $.validator.addMethod "balance", (value, element)->
    return backend.checkBalance(value, element)
  $.validator.addMethod "money", (value, element)->
    return backend.checkMoney(value, element)

  $("#withdraw-form").validate
    rules:
      amount:
        required: true
        money: true
        balance: true
      card_id:
        required: true

    messages:
      amount:
        required: '不能为空'
        money: '金额必须为正的两位小数'
        balance: '余额不足'
      card_id:
        required: '请选择银行卡'

  if $('#id-is-valid').val() == 'False'
    $('#id-validate').modal()
