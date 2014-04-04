require.config
  paths:
    jquery: 'lib/jquery.min'

require ['jquery', 'lib/backend'], ($, backend)->
  $('#validate_method').change (e)->
    selected = $(e.target).children('option:selected')[0]
    value = $(selected).val()
    console.log value

    if value == '手机'
      $('#email-form').hide()
      $('#phone-form').show()
    else if value == '邮箱'
      $('#email-form').show()
      $('#phone-form').hide()

  $('#sendMailButton').click (e)->
    target = $(e.target).attr('data-url')
    $.post target
    .done ->
      $('#sendMail').hide()
      $('#sendMailDone').show()
    .fail ->
      console.log 'Mail send failed'

  $('#sendValidateCodeButton').click (e)->
    target = $(e.target).attr('data-url')
    $.post target
    .done ->
      $('#nextStep').prop('disabled', false)

  $('#nextStep').click (e)->
    # Check the validate code first
    target = $(e.target).attr('data-url')
    validate_code = $('input[name="validate_code"]').val()
    $.post target, {
      "validate_code": validate_code
    }
    .done ->
      # If succeeded, then go to password setting page
      window.location = '/accounts/password/reset/set_password/'
    .fail ->
      console.log '验证失败!'
