import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName } from './mixins/api'
import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import { Trade, Deal_ui } from './mixins/trade_validation.js'
import 'polyfill'

(()=>{
    const
        $submit = $('button[type=submit]'),
        $idNumber = $('input[name=id_number]'),
        $bankCard = $('input[name=bankcard]'),
        $cardName = $('input[name=cardname]');

    //自动检查
    const autolist = [
        {target: $idNumber, required: true},
        {target: $bankCard, required: true},
        {target: $cardName, required: true}
    ];

    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
    });
    auto.operationClear()

    //验证表单
    const checkOperation = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'idCard', value: $idNumber.val()},
                    {type: 'bankCard', value: $bankCard.val()},
                    {type: 'isEmpty', value: $cardName.val()},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve({message: '验证成功'});

            signModel(sign);
            return reject('验证失败');
        })
    }

    const the_one_card = () => {
        ajax({
            type: 'get',
            url: '/api/pay/the_one_card/',
            success: function (data) {
                //同卡进出
                const cardName = data.bank.name;
                const cardNo = data.no.slice(-4);
                $('.bank-name').html(cardName)
                $('.bank-card').html(cardNo)
                $bankCard.attr('placeholder', `**${cardNo}（请输入完整卡号）`)
                $('.trade-warp').show()
            },
            error: function (data) {
                //没有同卡进出
                $('.unbankcard').show()
            },
            complete: function(){
                $('.recharge-loding').hide()
            }
        })
    }
    //设置交易密码
    const trade_set = (trade_operation, new_trade_pwd) => {
        const
            cardId = $bankCard.val(),
            citizenId = $idNumber.val();

        ajax({
            url: '/api/trade_pwd/',
            type: 'post',
            data: {
                action_type: 3,
                new_trade_pwd: new_trade_pwd,
                card_id : cardId,
                citizen_id: citizenId
            },
            success (result){
                let next = getQueryStringByName('next');
                next = next ='' ? '/weixin/list/' : next;
                if(result.ret_code == 0){
                    Deal_ui.show_alert('success', function(){
                        window.location = next;
                    })
                }

                if(result.ret_code > 0 ){
                    alert(result.message);
                }
            },
            complete: function(){
                trade_operation.loadingHide()
                trade_operation.destroy();
                trade_operation.layoutHide();
            }
        })
    }
    //交易密码
    const trade_operation = (callback) => {

        let set_trade_data = {};
        function set_trade(){
            const set_operation_1 = new Trade({
                header: '请输入新交易密码',
                explain: '请设置6位数字作为新交易密码',
                done: function (result) {
                    set_trade_data.password_1 = result.password
                    set_operation_1.destroy()
                    set_operation_1.layoutHide();
                    set_operation_2();
                }
            });
            set_operation_1.layoutShow();

            function set_operation_2(){
                const set_operation_2 = new Trade({
                    header: '请输入新交易密码',
                    explain: '请再次确认新交易密码',
                    done: function (result) {
                        set_trade_data.password_2 = result.password
                        if(set_trade_data.password_2 != set_trade_data.password_1){
                            set_operation_2.destroy()
                            set_operation_2.layoutHide()
                            return Deal_ui.show_alert('error', function(){
                                set_trade()
                            })
                        }
                        set_operation_2.loadingShow()

                        //设置交易密码
                        callback && callback(set_operation_2, result.password)

                    }
                });
                set_operation_2.layoutShow();
            }
        }

        set_trade()
    }



    the_one_card();

    $submit.on('click', function(){
        checkOperation()
            .then(()=>{
                console.log('验证成功'); //check success
                return trade_operation(trade_set);
            })
            .catch((message) => {
                console.log(message)
            })
    })

})()