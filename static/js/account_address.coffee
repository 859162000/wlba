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
    $('#address_id').val('')
    $('#address_name').val('')
    $('#phone_number').val('')
    $('#address_address').val('')
    $('#postcode').val('')
#    $('#default-checkbox').attr('checked', false)
    $('#add-address-submit').html('添加')
    $('span.modal-title').html('添加收货地址')

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
      address_id = $('#address_id').val()
      address_name = $('#address_name').val()
      phone_number = $('#phone_number').val()
      address_address = $('#address_address').val()
      postcode = $('#postcode').val()
      is_default = $('#default-checkbox').prop('checked')
      $.ajax {
        url: '/api/address/'
        data: {
          address_id: address_id
          name: address_name
          phone_number: phone_number
          address: address_address
          postcode: postcode
          is_default: is_default
        }
        type: 'POST'
      }
      .done ()->
        location.reload()
      .fail (xhr)->
        $.modal.close()
        result = JSON.parse xhr.responseText
        if result.ret_code
          tool.modalAlert({title: '温馨提示', msg: result.message})
        return
        tool.modalAlert({title: '温馨提示', msg: '地址添加失败'})

  _showModal = ()->
    $('#add-address-button').modal()

  $('.address_edit').click (e)->
    address_id = $(this).data("id")
    $('#add-address-submit').html('修改')
    $('span.modal-title').html('修改收货地址')
    $.ajax {
      url: "/api/address/"+ address_id + '/'
    }
    .done (data)->
      $('#add-address-button').modal()
      $('#address_id').val(data.address.address_id)
      $('#address_name').val(data.address.name)
      $('#phone_number').val(data.address.phone_number)
      $('#address_address').val(data.address.address)
      $('#postcode').val(data.address.postcode)
      if data.address.is_default == true
        $('#default-checkbox').attr('checked', true)
      else
        $('#default-checkbox').attr('checked', false)

  address_id = ""
  $('.address_delete').click (e)->
    address_id = $(this).data("id")
    tool.modalConfirm({title: '温馨提示', msg: '确定删除？', callback_ok: _deleteAddress})


  _deleteAddress = ()->
    $.ajax {
      url: '/api/address/delete/'
      data: {
        address_id: address_id
      }
      type: 'POST'
    }
    .done ()->
      location.reload()
    .fail (xhr)->
      $.modal.close()
      result = JSON.parse xhr.responseText
      if result.ret_code == 3003
        tool.modalAlert({title: '温馨提示', msg: result.message})
        return
      tool.modalAlert({title: '温馨提示', msg: '删除失败'})


