import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName } from './mixins/api'
import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import { Trade, Deal_ui } from './mixins/trade_validation.js'
import 'polyfill'


(() => {

    const
        $submit = $('button[type=submit]'),
        $amount = $('input[name=amount]'),
        $card_no = $("input[name='card_no']"),
        $loading = $(".recharge-loding"),
        $recharge_body =  $('.recharge-main'),
        $bank_name = $(".bank-txt-name");

    let tradeStatus = null;

    //自动检查
    const autolist = [
        {target: $amount, required: true}
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
                    {type: 'isEmpty', value: $amount.val()},
                    {type: 'isMoney', value: $amount.val()}
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) {
                return resolve({message: '验证成功', amount: $amount.val()});
            }

            signModel(sign);
            return console.log('验证失败');
        })
    }

    //confirm
    const confirm_ui = (amount) => {
        return new Promise((resolve, reject)=> {
            confirm(`充值金额为${amount}`, '确认充值', ()=> {
                resolve(amount)
            })
        })
    }
    const seachTrade = () => {
        ajax({
            url: '/api/profile/',
            type: 'GET',
            success: function(result){
                tradeStatus = result.trade_pwd_is_set ? true : false;
            }
        })
    }

    //设置交易密码
    const trade_set = (model_operation, new_trade_pwd) => {
        ajax({
            url: '/api/trade_pwd/',
            type: 'post',
            data: {
                action_type: 1,
                new_trade_pwd: new_trade_pwd
            },
            success (result){
                model_operation.loadingHide()
                model_operation.destroy()
                model_operation.layoutHide();
                if(result.ret_code == 0){
                    Deal_ui.show_alert('success', function(){
                        window.location = window.location.href;
                    },'交易密码设置成功，请牢记！')
                }

                if(result.ret_code > 0 ){
                    alert(result.message);
                }
            }
        })
    }
    //交易密码
    const trade_operation = (amount) => {
        tradeStatus ? entry_trade() : set_trade();

        function entry_trade(){
            const operation = new Trade({
                header: '请输入交易密码',
                explain: `充值金额<br>￥${amount}`,
                done: function (result) {
                    operation.loadingShow()

                    recharge(operation, result.password)
                }
            });
            operation.layoutShow();
        }

        let set_trade_data = {};
        function set_trade(){
                const set_operation_1 = new Trade({
                    header: '设置交易密码',
                    explain: '请设置6位数字作为交易密码',
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
                        header: '设置交易密码',
                        explain: '请再次确认交易密码',
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
                            trade_set(set_operation_2, result.password)

                        }
                    });
                    set_operation_2.layoutShow();
                }
            }
    }

    //渲染同卡进出的卡的卡片
    let dataCopy = null;
    const renderCard = (data) => {
        let card = data.no.slice(0, 6) + '********' + data.no.slice(-4);
        $loading.hide();
        $recharge_body.show();
        dataCopy = data;
        $amount.attr('placeholder', `该银行单笔限额${data.bank.bank_limit.second_one/10000}万元`);
        $card_no.val(card);
        $bank_name.text(data.bank.name);
    }

    //获取银行卡列表
    const fetchBanks = () => {
        ajax({
            url: '/api/pay/cnp/list_new/',
            type: 'POST',
            success (data) {
                if (data.ret_code === 0) {
                    $loading.hide();
                    data.cards.length === 0 ? $('.unbankcard').show() : $('.bankcard').show();
                }
                if (data.ret_code > 0 && data.ret_code != 20071) {
                    return alert(data.message);
                }
            },
            error (data) {
                return alert('系统异常，请稍后再试');
            }
        })
    }

    //判断是否有同卡绑定
    const the_one_card = () => {
        ajax({
            url: '/api/pay/the_one_card/',
            type: 'get',
            success (data) {
                //同卡进出
               renderCard(data);
               //判断是否设置交易密码
               seachTrade()
            },
            error (data) {
                //没有同卡进出
                if (data.status === 403) {
                    fetchBanks()
                }
            }
        });
    }
    //充值接口
    const recharge = (trade_operation, trade_pwd) => {
        const
            card = dataCopy.no.slice(0, 6) +  dataCopy.no.slice(-4),
            gate_id = dataCopy.bank.gate_id,
            amount = $amount.val() * 1;

        ajax({
            type: 'POST',
            url: '/api/pay/deposit_new/',
            data: {
                phone: '',
                card_no: card,
                amount: amount,
                gate_id: gate_id,
                trade_pwd: trade_pwd
            },
            beforeSend: function () {
                $submit.attr('disabled', true).text("充值中..");
            },
            success: function (result) {
                trade_operation.loadingHide()
                trade_operation.destroy();
                trade_operation.layoutHide();
                if(result.ret_code == 0){
                    return $('.sign-main').css('display', '-webkit-box').find(".balance-sign").text(result.amount);
                }

                if(result.ret_code == 30047){
                    return Deal_ui.show_entry(result.retry_count, function(){
                        trade_operation.layoutShow();
                    })
                }
                if(result.ret_code == 30048){
                    return Deal_ui.show_lock('取消', '找回密码', '交易密码已被锁定，请3小时后再试',function(){
                        window.location = '/weixin/trade-pwd/back/?next=/weixin/recharge/'
                    })
                }
                if (result.ret_code > 0) {
                    return alert(result.message);
                }
            },
            error: function (data) {
                if (data.status >= 403) {
                    alert('服务器繁忙，请稍后再试');
                }
            },
            complete: function () {
                $submit.removeAttr('disabled').text("充值");
            }
        })
    }

//-------------------逻辑处理
    the_one_card();

    $submit.on('click', () => {
        checkOperation()
            .then((result)=> {
                console.log(`验证成功，充值金额为${result.amount}`); //check success
                return confirm_ui(result.amount);
            })
            .then((amount)=> {
                //交易密码操作
                trade_operation(amount)
            })
            .catch((res) => {
               alert(res)
            })
    });
//---------------login操作end---------
})();