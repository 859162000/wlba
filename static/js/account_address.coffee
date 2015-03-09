require.config(
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.placeholder': 'lib/jquery.placeholder'
    'jquery.validate': 'lib/jquery.validate.min'
    tools: 'lib/modal.tools'

  shim:
    'jquery.modal': ['jquery']
    'jquery.placeholder': ['jquery']
    'jquery.validate': ['jquery']
)

require ['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder', 'jquery.validate', 'tools'], ($, modal, backend, placeholder, validate, tool)->
  $('input, textarea').placeholder()

  $('#add-address-button').click (e)->
    e.preventDefault()
    $(this).modal()

  $('#add-address-form').validate
    rules:
      address_name:
        required: true
      phone_number:
        required: true
      address_address:
        required: true

    messages:
      address_name:
        required: '收货人姓名不能为空'
      phone_number:
        required: '联系电话不能为空'
      address_address:
        required: '详细地址不能为空'

    errorPlacement: (error, element) ->
        error.appendTo $(element).parents('.form-row').children('.form-row-error')

    submitHandler: (form) ->
      address_name = $('#address_name').val()
      phone_number = $('#phone_number').val()
      address_address = $('#address_address').val()
      is_default = $('#default-checkbox').prop('checked')
      console.log(address_name+'//'+phone_number+'//'+address_address+'//'+is_default)
      $.ajax {
        url: '/api/address/add/'
        data: {
          name: address_name
          phone_number: phone_number
          address: address_address
          is_default: is_default
        }
        type: 'POST'
      }
      .done ()->
        console.log("$$$$$$$$$$$$")
        location.reload()
      .fail (xhr)->
        $.modal.close()
        result = JSON.parse xhr.responseText
        if result.error_code
          tool.modalAlert({title: '温馨提示', msg: result.message})
        return
        tool.modalAlert({title: '温馨提示', msg: '地址添加失败'})

  _showModal = ()->
    $('#add-card-button').modal()

  address_id = ""
  $('a#delete_address').click (e)->
    address_id = $(this).attr("address_id")
    tool.modalConfirm({title: '温馨提示', msg: '确定删除？', callback_ok: _deleteAddress})

  _deleteAddress = ()->
    $.ajax {
      url: '/api/address/delete/' + address_id + '/'
      data: {
        address_id: address_id
      }
    }
    .done ()->
      location.reload()
    .fail (xhr)->
      $.modal.close()
      result = JSON.parse xhr.responseText
      if result.error_code == 5
        tool.modalAlert({title: '温馨提示', msg: result.message})
        return
      tool.modalAlert({title: '温馨提示', msg: '删除失败'})


