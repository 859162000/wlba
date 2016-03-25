// Generated by CoffeeScript 1.8.0
(function () {

    require(['jquery', 'tools', 'csrf'], function ($, tool) {

        var $submit = $('.c-blue-button');
        var token = '';
        $submit.on('click', function(){
            token = $.trim($('input[name="token"]').val());

            if(token == '') {
                return tool.modalAlert({
                    title: '温馨提示',
                    msg: '兑换码不能为空'
                });
            }

            var posting = $.post( '/api/redpacket/exchange/', { token: token } );

            posting
                .done(function(data){
                    if (data.ret_code === 0) {
                        return tool.modalAlert({
                            btnText: "确认",
                            title: '温馨提示',
                            msg: '兑换成功',
                            callback_ok: function () {
                                return window.location.reload();
                            }
                        });
                    } else {
                        return tool.modalAlert({
                            btnText: "确认",
                            title: '温馨提示',
                            msg: data.message
                        });
                    }
                })
                .fail(function(data){
                    return tool.modalAlert({
                        btnText: "确认",
                        title: '温馨提示',
                        msg: '服务器忙，请稍后重试'
                    });
                })

        });
    });

}).call(this);