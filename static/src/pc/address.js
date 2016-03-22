(function () {

    require(['jquery', 'tools', 'jquery.validate', 'csrf'], function ($, tool) {

        var $addressMask = $('.c-profile-mask'),
            $address = $('.c-profile-alert'),
            $add = $('.add-address'),
            $edit = $('.edit-address'),
            $delete = $('.delete-add'),
            $ID = $('input[name=address_id]'),
            $addressName = $('input[name=address_name]'),
            $addressNumber = $('input[name=phone_number]'),
            $addressDetail = $('input[name=address_address]'),
            $default = $('input[name=default_checkbox]'),
            $submit = $('input[type=submit]');

        $add.on('click', function () {
            $(this).modal();
            $ID.val('');
            $addressNumber.val('');
            $addressName.val('');
            $addressDetail.val('');
            $submit.val('确认添加');
        });

        $edit.on('click', function () {
            $(this).modal();
            $ID.val($(this).data('id'));
            $addressNumber.val($(this).data('phone'));
            $addressName.val($(this).data('name'));
            $addressDetail.val($(this).data('address'));
            $submit.val('确认修改');
            $(this).data('default') === 'True' ? $default.attr('checked', true) : $default.attr('checked', false);
        });

        var addressID = null;
        $delete.on('click', function () {
            addressID = $(this).data("id");
            return tool.modalConfirm({
                title: '温馨提示',
                msg: '确定删除？',
                callback_ok: _deleteAddress
            });
        });
        $('#add-address-form').validate({
            focusInvalid: false,
            rules: {
                address_name: {
                    required: true
                },
                phone_number: {
                    required: true,
                },
                address_address: {
                    required: true
                }
            },
            messages: {
                address_name: {
                    required: '收货人姓名不能为空'
                },
                phone_number: {
                    required: '联系电话不能为空'
                },
                address_address: {
                    required: '详细地址不能为空'
                }
            },
            errorPlacement: function (error, element) {
                return error.appendTo($(element).parents('.form-row').children('.form-row-error'));
            },
            submitHandler: function (form) {
                var
                    address_id = $ID.val(),
                    name = $addressName.val(),
                    phone_number = $addressNumber.val(),
                    address = $addressDetail.val(),
                    is_default = $default.prop('checked');
                var push = $.post('/api/address/', {
                    address_id: address_id,
                    name: name,
                    phone_number: phone_number,
                    address: address,
                    is_default: is_default
                })

                push
                    .done(function () {
                        return location.reload();
                    })
                    .fail(function (xhr) {

                        var result = JSON.parse(xhr.responseText);
                        $.modal.close();
                        if (result.ret_code) {
                            return tool.modalAlert({
                                title: '温馨提示',
                                msg: result.message
                            });
                        }
                        return tool.modalAlert({
                            title: '温馨提示',
                            msg: '地址添加失败'
                        });
                    });
            }
        });

        var _deleteAddress = function () {

            $.post('/api/address/delete/', {address_id: addressID})
                .done(function () {
                    return location.reload();
                })
                .fail(function (xhr) {
                    var result;
                    $.modal.close();
                    result = JSON.parse(xhr.responseText);
                    if (result.ret_code === 3003) {
                        tool.modalAlert({
                            title: '温馨提示',
                            msg: result.message
                        });
                        return;
                    }
                    return tool.modalAlert({
                        title: '温馨提示',
                        msg: '删除失败'
                    });
                })
        }

    });

}).call(this);