import './mixins/ui.js'
import {ajax } from './mixins/api'


(()=>{

    const
        $set_bank = $('.set-bank'),
        $set_bank_sig  = $('.set-bank-sign'),
        $bank_cancel  = $('.bank-cancel'),
        $bank_confirm =  $('.bank-confirm'),
        $name = $('.name'),
        $no = $('.no');

    $set_bank.on('click', function(){
        const
            id = $(this).attr('data-id'),
            no = $(this).attr('data-no'),
            name = $(this).attr('data-name');

        $set_bank_sig.show()
        $name.text(name)
        $no.text(no.slice(-4))
        $bank_confirm.attr('data-id', id)
    })

    $bank_cancel.on('click', function(){
        $set_bank_sig.hide()
    })

    $bank_confirm.on('click', function(){
        var id = $(this).attr('data-id')
        putBank(id)
    })


    function putBank(id){
        const $set_bank_sig  = $('.set-bank-sign');
        ajax({
            type: 'put',
            url: '/api/pay/the_one_card/',
            data: {
                card_id: id
            },
            beforeSend () {
                $('.bank-confirm').text('绑定中...').attr('disabled', true);
            },
            success (data) {
                if(data.status_code === 0 ){
                    $set_bank_sig.hide();
                    return alert('绑定成功', function(){
                        var url  = window.location.href;
                        window.location.href = url;
                    })
                }
            },
            error (xhr) {
                $set_bank_sig.hide();
                var result = JSON.parse(xhr.responseText);
                return alert(result.detail+ '，一个账号只能绑定一张卡')
            },
            complete (){
                $('.bank-confirm').text('立即绑定').removeAttr('disabled');
            }
        })
    }
})()