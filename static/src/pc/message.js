(function () {

    require(['jquery', 'tools', 'jquery.validate', 'csrf'], function ($, tool) {
        var $message = $('.c-message-table tbody tr');

        $message.on('click', function(){
            var id = $(this).data('msg-id');

            $(this).addClass('read-active');
            $(this).find('.msg-cont').toggle();

            if($(this).find('.iconfont').hasClass('icon-circle-add')){
                $(this).find('.iconfont').removeClass('icon-circle-add').addClass('icon-remove')
            }else{
                $(this).find('.iconfont').removeClass('icon-remove').addClass('icon-circle-add')
            }

            if ($(this).data('read-status') === 'False') {
                readMessage(id)
            }
        });

        var readMessage = function(msg_id){
            $.post('/accounts/message/' + msg_id + '/')
                .done(function(){
                    return $('#' + msg_id).attr('data-read-status', 'True');
                })
        }
    });

}).call(this);