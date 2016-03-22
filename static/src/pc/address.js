(function () {

    require(['jquery', 'tools', 'jquery.validate', 'csrf'], function ($, tool) {

        var $addressMask = $('.c-profile-mask'),
            $address = $('.c-profile-alert'),
            $add = $('.add-address'),
            $edit = $('.edit-address');

        var renderAlert = function (type, id, data) {
            
        };

        $add.on('click', function () {
            $(this).modal();
        });

        $edit.on('click', function () {

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
                return console.log(form)
            }
        });


    });

}).call(this);