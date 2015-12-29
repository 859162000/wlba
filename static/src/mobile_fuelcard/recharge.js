import './mixins/ui'
import { Automatic } from './mixins/automatic_detection'
import { ajax, signView } from './mixins/functions'

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
        return new Promise((resolve, reject)=>{
            ajax({
                url:'/api/pay/cnp/list_new/',
                type: 'POST',
                success(result){
                    $('.recharge-loding').hide()
                    if(result.ret_code === 0 ){
                        resolve(result.cards)
                    }

                    if (result.ret_code > 0 && result.ret_code != 20071) {
                        return reject(data.message);
                    }
                },
                error(result){
                    reject('系统异常，请稍后再试')
                }
            })
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
                    return signView(results.message);
                } else {
                   return signView('充值成功')
                }
            },
            error: function (results) {
                if (results.status >= 403) {
                    signView('服务器繁忙，请稍后再试');
                }
            },
            complete: function () {
                $submit.removeAttr('disabled').text("立即充值");
            }
        })
    }

    /**
     * 判断有无同卡进出卡，有的话充值，没有做相应跳转
     */
    on_card()
        .then((result)=>{
            //有同卡
            on_card_operation(result);
        })
        .catch((result)=>{
            //无同卡
            return banl_list()
        })
        .then((result)=>{
            //有无银行卡
            result.length === 0 ? $('.unbankcard').show() : $('.bankcard').show();
        })
        .catch((result)=>{
            //banl_list 异常捕捉
            if(result){
                return signView(result)
            }
            return signView('系统异常')



        })

    $submit.on('click', ()=> {
        var
            AMOUNT = $amount.val() * 1;

        if (AMOUNT == 0 || !AMOUNT) {
            return signView('请输入充值金额')
        }
        const push_data = {
            phone: '',
            card_no: g_CARD,
            amount: AMOUNT,
            gate_id: g_GATE_ID,
        }
        confirm("充值金额为" + AMOUNT, '确认充值', recharge, push_data)
    })

})()