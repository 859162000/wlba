import { ui_alert, ui_signError, ui_confirm} from './mixins/ui'
import { Automatic } from './mixins/automatic_detection'
import { ajax } from './mixins/functions'

(()=>{
    const
        $item = $('.fuel-recharge-warp'),
        $bankName = $('.recharge-bank'),
        $bankCard = $('.recharge-card'),
        $amount = $('input[name=amount]'),
        $submit = $('button[type=submit]');
    let g_CARD = null,  g_GATE_ID = null, g_AMOUNT = null ;

    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: [
            {target: $amount, required: true},
        ]
    });
    auto.operation();

    const on_card = () => {
        return new Promise((resolve, reject)=>{
            ajax({
                url:'/api/pay/the_one_card/',
                type: 'GET',
                success(result){
                    $('.recharge-loding').hide()
                    resolve(result)
                },
                error(result){
                    reject(result)
                }
            })
        })
    }

    const on_card_operation = (data) => {
        const card = data.no.slice(0, 6) + '********' + data.no.slice(-4), name =  data.bank.name;
        [ g_CARD, g_GATE_ID ] = [data.no.slice(0, 6)+ data.no.slice(-4), data.bank.gate_id];

        $item.show();
        $bankCard.text(card)
        $bankName.text(name)
    }

    const banl_list = () => {
        ajax({
            url:'/api/pay/cnp/list_new/',
            type: 'POST',
            success(result){
                $('.recharge-loding').hide()
                if(result.ret_code === 0 ){
                    result.cards.length === 0 ? $('.unbankcard').show() : $('.bankcard').show();
                }

                if (result.ret_code > 0 && result.ret_code != 20071) {
                    return ui_signError(data.message);
                }
            },
            error(result){
                ui_signError('系统异常，请稍后再试')
            }
        })
    }

    const recharge = (data) => {
        ajax({
            type: 'POST',
            url: '/api/pay/deposit_new/',
            data: data,
            beforeSend: function () {
                $submit.attr('disabled', true).text("充值中..");
            },
            success: function (results) {
                if (results.ret_code > 0) {
                    return ui_signError(results.message);
                } else {
                   return ui_alert('充值成功')
                }
            },
            error: function (results) {
                if (results.status >= 403) {
                    ui_signError('服务器繁忙，请稍后再试');
                }
            },
            complete: function () {
                $submit.removeAttr('disabled').text("立即充值");
            }
        })
    }

    /**
     * 判断有无同卡进出卡，有的话充值，没有做相应处理
     */
    on_card()
        .then((result)=>{
            //有同卡
            on_card_operation(result);
        })
        .catch(()=>{
            //无同卡
            return banl_list()
        })


    $submit.on('click', ()=> {
        var
            AMOUNT = $amount.val() * 1;

        if (AMOUNT == 0 || !AMOUNT) {
            return ui_signError('请输入充值金额')
        }
        const push_data = {
            phone: '',
            card_no: g_CARD,
            amount: AMOUNT,
            gate_id: g_GATE_ID,
        }
        ui_confirm("充值金额为" + AMOUNT, '确认充值', recharge, push_data)
    })

})()