import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName, calculate } from './mixins/api'
import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import { Trade, Deal_ui } from './mixins/trade_validation.js'


(() => {

    const
        $submit = $('button[type=submit]'),
        $inputCalculator = $('input[data-role=p2p-calculator]'),
        $repack = $('select[name=redpack]');

    const $redpackSign =$('.redpack-sign');
    const $showAmount = $('.need-amount');
    const $showredPackAmount =$(".redpack-amount");
    const $redpackInvestamount = $(".redpack-investamount");


    const repackSelect = (inputTarget, _self) => {
        let selectOption = _self.find('option').eq(_self.get(0).selectedIndex),
            selectAmount = parseFloat(selectOption.attr('data-amount')),
            inputTargetAmount = parseInt(inputTarget.val()),
            redPackAmount = selectOption.attr("data-amount"), //红包金额
            redPackMethod = selectOption.attr("data-method"), //红包类型
            redPackInvestamount = parseInt(selectOption.attr("data-investamount")),//红包门槛
            redPackHighest_amount = parseInt(selectOption.attr("data-highest_amount")),//红包最高抵扣（百分比红包才有）
            repPackDikou = 0, //抵扣金额
            senderAmount = 0; //实际支付金额;
        let redPackAmountNew = 0;


        $redpackForAmount.hide()
        $redpackSign.hide()
        $redpackInvestamount.hide()

        if (inputTargetAmount < redPackInvestamount) {
            return $redpackInvestamount.show();//未达到红包使用门槛
        }

        if(inputTargetAmount >= redPackInvestamount){
            $inputCalculator.attr('activity-jiaxi', 0);
            if (redPackMethod == '*') {
                //百分比红包
                if (inputAmount * redPackAmount >= redPackHighest_amount && redPackHighest_amount > 0) {//是否超过最高抵扣
                    repPackDikou = redPackHighest_amount;
                } else {//没有超过最高抵扣
                    repPackDikou = inputAmount * redPackAmount;
                }
            } else if (redPackMethod == '~') {//加息券
                $inputCalculator.attr('activity-jiaxi', redPackAmount * 100);
                repPackDikou = 0;
            } else {  //直抵红包
                repPackDikou = parseInt(redPackAmount);
            }

            senderAmount = inputAmount - repPackDikou; //实际支付金额

            //lib.redPackAmountNew = repPackDikou; 抵扣金额保存
            if (redPackMethod != '~') {
                $showredPackAmount.text(repPackDikou);//红包抵扣金额
                $showAmount.text(senderAmount);//实际支付金额
                $redpackSign.show();//红包直抵提示
            }
        }

    }
//---------------初始化操作start---------
    const autolist = [
            {target: $inputCalculator, required: true},
            {target: $repack, required: true, callback: function(){
                repackSelect($inputCalculator, $repack)
            }},
        ];

    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
        done: function(status){
            console.log($inputCalculator)
            calculate.operation($inputCalculator)
        }
    });




//---------------初始化操作end---------

})();