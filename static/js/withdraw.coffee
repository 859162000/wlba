require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.placeholder': 'lib/jquery.placeholder'

  shim:
    'jquery.modal': ['jquery']
    'jquery.placeholder': ['jquery']
)

require ['jquery'], ($)->
  $('#withdraw').click (e)->
    e.preventDefault()
    amount = $('#amount').val()
    $.ajax {
      url: '/api/withdraw/'
      data: {
        amount: amount
      }
      type: 'post'
    }
    .done (json)->
        form = $('#huifu-form')
        while form.firstChild
          form.removeChild(form.firstChild)
        for name, value of json['form']['post']
          input = $('<input>').attr('type', 'hidden').attr('name', name).val(value)
          $('#huifu-form').append($(input))
        $('#huifu-form').attr('action', json['form']['url'])
        $('#huifu-form').submit()

  $('#add-card-button').click ()->
    $(this).modal()

