require.config(
  paths:
    jquery: 'lib/jquery.min'
)

require ['jquery'], ($)->
  $('#pay').click (e)->
    e.preventDefault()
    amount = $('#amount').val()
    gate_id = $('#gate_id').val()
    $.ajax {
      url: '/api/pay/'
      data: {
        amount: amount
        gate_id: gate_id
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

