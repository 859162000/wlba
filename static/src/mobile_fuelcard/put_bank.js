import { ui_alert, ui_signError} from './mixins/ui'
import { ajax } from './mixins/functions'


(()=>{
    const
        $setBank = $('.set-bank'),
        $signItem = $('.set-bank-sign'),
        $confirm = $('.bank-confirm');


    var put_bank = (id)=> {
        ajax({
            type: 'put',
            url: '/api/pay/the_one_card/',
            data: {
                card_id: id
            },
            beforeSend: function () {
                $confirm.text('绑定中...').attr('disabled', true);
            },
            success: function (data) {
                if(data.status_code === 0 ){
                    $signItem.hide()
                    return ui_alert('绑定成功', function(){
                        var url  = window.location.href;
                        window.location.href = url;
                    })
                }
            },
            error: function (xhr) {
                $signItem.hide()
                var result = JSON.parse(xhr.responseText);
                return ui_signError(result.detail+ '，一个账号只能绑定一张卡')
            },
            complete: function(){
                $confirm.text('立即绑定').removeAttr('disabled');
            }
        })
    }

    $setBank.on('click', function() {
        const
            bank_id = $(this).attr('data-id'),
            bank_name = $(this).attr('data-name'),
            bank_no = $(this).attr('data-no');


        $signItem.find('.name').html(bank_name)
        $signItem.find('.no').html(bank_no)
        $confirm.attr('data-id', bank_id)
        $signItem.show();
    })

    $confirm.on('click', function() {
        const bank_id = $(this).attr('data-id');
        put_bank(bank_id)
    })

    $('.bank-cancel').on('click', function() {
       $signItem.hide()
    })

})()