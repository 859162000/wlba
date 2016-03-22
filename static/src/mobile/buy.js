import './mixins/promise'
import { Automatic } from './mixins/automatic_detection'
import { ajax, calculate } from './mixins/api'
import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import { Trade, Deal_ui } from './mixins/trade_validation.js'
import 'polyfill'


(() => {

    const
        $submit = $('button[type=submit]'),
        $inputCalculator = $('input[data-role=p2p-calculator]'),
        $repack = $('select[name=redpack]'),
        $redpackSign =$('.redpack-sign'),
        $showAmount = $('.need-amount'),
        $showredPackAmount =$(".redpack-amount"),
        $redpackInvestamount = $(".redpack-investamount"),
        productID = $(".invest-one").attr('data-protuctid'),
        $alreadyReadPack = $('.redpack-already'),
        $buySufficient = $('.buy-sufficient');
    let tradeStatus = null,
        redPackDikouCopy = 0; //抵扣金额－全局

    //检测select
    const repackSelect = (inputTarget, _self) => {
        let selectOption = _self.find('option').eq(_self.get(0).selectedIndex),
            inputTargetAmount = parseInt(inputTarget.val()) || 0,
            redPackAmount = selectOption.attr("data-amount"), //红包金额
            redPackMethod = selectOption.attr("data-method"), //红包类型
            redPackInvestamount = parseInt(selectOption.attr("data-investamount")),//红包门槛
            redPackHighest_amount = parseInt(selectOption.attr("data-highest_amount")),//红包最高抵扣（百分比红包才有）
            repPackDikou = 0, //抵扣金额
            senderAmount = 0; //实际支付金额;

            redPackDikouCopy = 0;  //抵扣金额全局


        $redpackSign.hide()
        $redpackInvestamount.hide()

        if (inputTargetAmount < redPackInvestamount) {
            return $redpackInvestamount.show();//未达到红包使用门槛
        }

        if(inputTargetAmount >= redPackInvestamount){
            $inputCalculator.attr('activity-jiaxi', 0);
            if (redPackMethod == '*') {
                //百分比红包
                if (inputTargetAmount * redPackAmount >= redPackHighest_amount && redPackHighest_amount > 0) {//是否超过最高抵扣
                    repPackDikou = redPackHighest_amount;
                } else {//没有超过最高抵扣
                    repPackDikou = inputTargetAmount * redPackAmount;
                }
            } else if (redPackMethod == '~') {//加息券
                $inputCalculator.attr('activity-jiaxi', redPackAmount * 100);
                repPackDikou = 0;
            } else {  //直抵红包
                repPackDikou = parseInt(redPackAmount);
            }

            senderAmount = inputTargetAmount - repPackDikou; //实际支付金额

            redPackDikouCopy = repPackDikou; //抵扣金额保存
            if (redPackMethod != '~') {
                $showredPackAmount.text(repPackDikou);//红包抵扣金额
                $showAmount.text(senderAmount);//实际支付金额
                $redpackSign.show();//红包直抵提示
            }
        }

    }

    //投资历史
    const investHistory = () => {
        return new Promise((resolve, reject)=>{
            ajax({
                type: 'POST',
                url: '/api/redpacket/selected/',
                data: { product_id: productID},
                success (data) {
                    if (data.ret_code === 0) {
                        if (data.used_type == 'redpack')
                            $alreadyReadPack.html(data.message).show();
                        else if (data.used_type == 'coupon') {
                            $inputCalculator.attr('activity-jiaxi', data.amount);
                            $alreadyReadPack.show().find('.already-amount').text(data.amount + '%');

                            return resolve('重新计算收益')
                        }
                    }
                    if($inputCalculator.val() > 0) return resolve('重新计算收益')
                    reject('不需要重新计算收益')
                },
                error(){
                    reject('不需要重新计算收益');
                }
            });
        })
    }

    //检测交易密码
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
    const trade_operation = (amount, callback) => {
        tradeStatus ? entry_trade() : set_trade();

        function entry_trade(){
            const operation = new Trade({
                header: '请输入交易密码',
                explain: `投资金额<br>￥${amount}`,
                done: function (result) {
                    operation.loadingShow()
                    callback && callback(operation, result.password, amount)
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

    //购买
    const buy = (trade_operation, trade_pwd, investAmount) => {
        const
            balance = parseFloat($("#balance").attr("data-value")),
            redPackValue = $repack.val() == '' ? null :  $repack.val();

        ajax({
            type: 'POST',
            url: '/api/p2p/purchase/mobile/',
            data:  {
                amount: investAmount,
                product: productID,
                redpack: redPackValue,
                trade_pwd: trade_pwd
            },
            beforeSend: function () {
                $submit.attr('disabled',true).text("抢购中...");
            },
            success: function(result){
                trade_operation.loadingHide()
                trade_operation.destroy();
                trade_operation.layoutHide();
                if(result.ret_code == 0){
                    $('.balance-sign').text(balance - result.data + redPackDikouCopy + '元');
                    $(".sign-main").css("display","-webkit-box");
                    return
                }

                if(result.ret_code == 30047){
                    Deal_ui.show_entry(result.retry_count, function(){
                        trade_operation.layoutShow();
                    })
                    return
                }
                if(result.ret_code == 30048){
                    Deal_ui.show_lock('取消', '找回密码', '交易密码已被锁定，请3小时后再试',function(){
                        window.location = `/weixin/trade-pwd/back/?next=/weixin/view/buy/${productID}/`;
                    });
                    return
                }
                if(result.error_number > 0){
                    return alert(result.message);
                }
            },
            error: function (xhr) {
                alert('服务器异常');
            },
            complete: function () {
                $submit.removeAttr('disabled').text("立即投资");
            }
        })
    }

    //自动检查,计算器
    const auto = new Automatic({
        submit: $submit,
        checklist: [
            {target: $inputCalculator, required: true},
            {target: $repack, required: false}
        ],
        done: function(status){
            //触发自动检测之后的回调(计算收益)
            repackSelect($inputCalculator, $repack)
            calculate.operation($inputCalculator)
        }
    });

    //验证表单
    const checkOperation = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'isEmpty', value: $inputCalculator.val()},
                    {type: 'money100', value: $inputCalculator.val()}
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve({message: '验证成功', amount: $inputCalculator.val()});

            signModel(sign);
            return console.log('验证失败');
        })
    }
    const balance = (amount) => {
        return new Promise((resolve,reject)=>{
            const balance = parseFloat($("#balance").attr("data-value"));
            if (amount > balance){
                return $buySufficient.show();
            }
            $buySufficient.hide();
            resolve(amount)
        })

    }
    //confirm
    const confirm_ui = (amount) => {
        return new Promise((resolve, reject)=> {
            confirm(`购买金额为${amount}`, '确认投资', ()=> {
                resolve(amount)
            })
        })
    }
//---------------初始化操作start---------

    //判断是否使用过理财券
    investHistory()
        .then((result)=>{
            console.log(result)
            $inputCalculator.trigger('input');
        })
        .catch((result)=>{
            console.log(result)
        })
        .done(()=>{
            console.log('查询是否设置过交易密码')
            seachTrade();
        })

    //提交逻辑操作
    $submit.on('click', () => {
        checkOperation()
            .then((result)=> {
                return balance(result.amount);
            })
            .then((amount)=> {
                return confirm_ui(amount);
            })
            .then((amount)=> {
                //交易密码操作
                trade_operation(amount, buy)
            })
            .catch((res) => {
               alert(res)
            })
    });

//---------------初始化操作end---------

})();