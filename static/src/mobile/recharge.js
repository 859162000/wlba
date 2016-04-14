import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName } from './mixins/api'
import { Alert, Confirm, signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import { Trade, Deal_ui } from './mixins/trade_validation.js'


(() => {

    const
        $submit = $('button[type=submit]'),
        $amount = $('input[name=amount]'),
        $card_no = $("input[name='card_no']"),
        $loading = $(".recharge-loding"),
        $recharge_body =  $('.recharge-main'),
        $validate_code = $('input[name=validate_code]'),
        $validate_operation = $('button[name=validate_operation]'),
        $bank_name = $(".bank-txt-name");

    let tradeStatus = null;

    let need_validation_for_qpay = null;
    let order_data = null;

    //自动检查

    const func_auto = (validation) => {
        const autolist = [
            {target: $amount, required: true},
        ];

        if(validation){
            autolist.push({target: $validate_code, required: true})
        }

        const auto = new Automatic({
            submit: $submit,
            checklist: autolist,
        });
        auto.operationClear();
    }

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

    const checkOperation_code = () => {
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
            Confirm(`充值金额为${amount}`, '确认充值', ()=> {
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
                    Alert(result.message);
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

                    let options = {
                        data: {},
                        beforeSend(){
                            $submit.attr('disabled', true).text("充值中..");
                        },
                        success(result) {

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
                                return Alert(result.message);
                            }
                        },
                        error(data) {
                            if (data.status >= 403) {
                                Alert('服务器繁忙，请稍后再试');
                            }
                        },
                        complete (trade_operation) {
                            if(trade_operation){
                                trade_operation.loadingHide();
                                trade_operation.destroy();
                                trade_operation.layoutHide();
                            }
                            $submit.removeAttr('disabled').text("充值");
                        }
                    };

                    if(need_validation_for_qpay){
                        //需要短信
                        options.data = {
                            phone: '',
                            vcode: $validate_code.val(),
                            order_id: order_data.order_id,
                            token: order_data.token,
                            set_the_one_card: false,
                            trade_pwd: result.password,
                            mode: 'qpay_with_sms'
                        }
                        recharge(options, operation)

                    }else{
                        //不需要短信
                        options.data = {
                            phone: '',
                            card_no: $card_no.attr('data-bank'),
                            amount: $amount.val(),
                            gate_id: $card_no.attr('data-id'),
                            trade_pwd: result.password,
                        };
                        recharge_or_code(options, operation);
                    }
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
                        let re = /^\d{6}$/;
                        set_trade_data.password_1 = result.password;
                        if(!re.test(result.password)){
                            return signModel("请设置6位数字作为交易密码");
                        }
                        set_operation_1.destroy();
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
                            set_trade_data.password_2 = result.password;
                            if(set_trade_data.password_2 != set_trade_data.password_1){
                                set_operation_2.destroy();
                                set_operation_2.layoutHide();
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
        $card_no.val(card).attr({'data-bank': data.no.slice(0, 6) + data.no.slice(-4), 'data-id': data.bank.gate_id});
        $bank_name.text(data.bank.name);
        //初始化表单自动检查

        if(data.need_validation_for_qpay){
            $('.wx-input-double').show()
            func_auto(true);
            need_validation_for_qpay = true
        }else{
            func_auto(false);
        }


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
                    return Alert(data.message);
                }
            },
            error (data) {
                return Alert('系统异常，请稍后再试');
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
    const recharge_or_code = (options, trade_operation) => {

        ajax({
            type: 'POST',
            url: '/api/pay/deposit_new/',
            data: options.data,
            beforeSend () {
                options.beforeSend && options.beforeSend()
                //$submit.attr('disabled', true).text("充值中..");
            },
            success (result) {

                options.success && options.success(result);
                //trade_operation.loadingHide();
                //trade_operation.destroy();
                //trade_operation.layoutHide();
                //if(result.ret_code == 0){
                //    return $('.sign-main').css('display', '-webkit-box').find(".balance-sign").text(result.amount);
                //}
                //
                //if(result.ret_code == 30047){
                //    return Deal_ui.show_entry(result.retry_count, function(){
                //        trade_operation.layoutShow();
                //    })
                //}
                //if(result.ret_code == 30048){
                //    return Deal_ui.show_lock('取消', '找回密码', '交易密码已被锁定，请3小时后再试',function(){
                //        window.location = '/weixin/trade-pwd/back/?next=/weixin/recharge/'
                //    })
                //}
                //if (result.ret_code > 0) {
                //    return Alert(result.message);
                //}
            },
            error (data) {
                options.error && options.error(data);

                //if (data.status >= 403) {
                //    Alert('服务器繁忙，请稍后再试');
                //}
            },
            complete () {
                options.complete && options.complete(trade_operation);
                //$submit.removeAttr('disabled').text("充值");
            }
        })
    }
    const recharge = (options, trade_operation) => {
        ajax({
            type: 'POST',
            url: '/api/pay/cnp/dynnum_new/',
            data: options.data,
            beforeSend () {
                options.beforeSend && options.beforeSend()
            },
            success (result) {
                options.success && options.success(result);
            },
            error (data) {
                options.error && options.error(data);
            },
            complete () {
                options.complete && options.complete(trade_operation);
            }
        })
    }

    //倒计时
    let timeIntervalId = null;
    const  timerFunction = (count) => {
        return new Promise((resolve, reject)=> {
            var timerFunction = function () {
                if (count > 1) {
                    count--;
                    return $validate_operation.text(`${count}秒后可重发`);
                } else {
                    clearInterval(timeIntervalId);
                    timeIntervalId = null;
                    $validate_operation.text('重新获取').removeAttr('disabled');
                    return reject('倒计时失效，请重新获取')
                }
            };
            timerFunction();
            return timeIntervalId = setInterval(timerFunction, 1000);
        })
    }
//-------------------逻辑处理
    the_one_card();

    $validate_operation.on('click', () => {
        checkOperation_code()
            .then((result) => {
                const options = {
                    data: {
                        card_no: $card_no.attr('data-bank'),
                        amount: $amount.val(),
                        gate_id: $card_no.attr('data-id'),
                        mode: 'vcode_for_qpay'
                    },
                    beforeSend(){
                        $validate_operation.attr('disabled', 'disabled').text('发送中..')
                    },
                    success(result) {
                        if(result.ret_code == 0){
                            signModel('短信已发送，请注意查收！');
                            order_data = {
                                token: result.token,
                                order_id: result.order_id
                            };
                            let count = 60;
                            return timerFunction(count).catch((res) => signModel(res))

                        }
                    },
                    error(xhr) {
                        var result = JSON.parse(xhr.responseText);
                        $validate_operation.removeAttr('disabled').text('获取验证码');
                        clearInterval(timeIntervalId);
                        timeIntervalId = null;
                        return signModel(result.message);
                    }
                };
                return recharge_or_code(options);
            })
            .catch((res) => {
               signModel(res)
            })
    });

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
               Alert(res)
            })
    });
//---------------login操作end---------
})();