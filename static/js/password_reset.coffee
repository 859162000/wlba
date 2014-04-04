require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  $('#submitButton').click (e)->
    e.preventDefault()

    url = $('form#identifier').attr 'action'
    identifier = $('input[name="identifier"]').val()
    backend.userExists identifier
    .done ->
      $('form#identifier').submit()
    .fail ->
      alert '用户不存在'



