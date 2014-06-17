require.config(
  paths:
    jquery: 'lib/jquery.min'
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

