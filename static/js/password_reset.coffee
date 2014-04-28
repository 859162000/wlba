require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  submit_form = ()->
    identifier = $('input[name="identifier"]').val()
    backend.userExists identifier
    .done ->
      $('form#identifier').submit()
      return true
    .fail ->
      alert '用户不存在'

  $('#submitButton').click (e)->
    e.preventDefault()
    submit_form()

  $('input').keyup (e)->
    if e.keyCode == 13
      e.preventDefault()
      submit_form()

