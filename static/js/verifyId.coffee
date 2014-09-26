require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.validate': 'lib/jquery.validate.min'
    tools: 'lib/modal.tools'

  shim:
    'jquery.modal': ['jquery']
    'jquery.validate': ['jquery']
)

require ['jquery', 'lib/modal', 'lib/backend', 'jquery.validate', 'tools'], ($, modal, backend, validate, tool)->

  $.validator.addMethod 'idNumber', (value, element)->
    reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
    return reg.test(value)
  , '请输入有效身份证'

  $('#validate_id_form').validate
    rules:
      name:
        required: true
      id_number:
        required: true
        idNumber: true

    messages:
      name:
        required: '请输入姓名'
      id_number:
        required: '请输入身份证'
        idNumber: '请输入有效身份证'

    errorPlacement: (error, element) ->
      error.appendTo $(element).closest('.form-row').find('.form-row-error')


    submitHandler: (form)->
      name = $('#id_name').val()
      id_number = $('#id_id_number').val()
      if $("#validate_id_button").hasClass "disabled"
        return;
      $("#validate_id_button").addClass('disabled')
      $.ajax {
        url: '/api/id_validate/'
        data: {
          name: name
          id_number: id_number
        }
        type: 'post'
      }
      .done ()->
        tool.modalAlert({title: '温馨提示', msg: '实名认证成功', callback_ok: ()->
          location.reload()
        })

      .fail (xhr)->
        ("#validate_id_button").removeClass "disabled"
        result = JSON.parse xhr.responseText
        if result.error_number == 8
          tool.modalAlert({title: '温馨提示', msg: result.message})
          return
        else if result.error_number == 9
          tool.modalAlert({title: '温馨提示', msg: result.message})


        tool.modalAlert({title: '温馨提示', msg: result.message})
