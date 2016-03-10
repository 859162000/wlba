import { calculate  } from './mixins/api'
import { signModel } from './mixins/ui.js'

(() => {

    const
        $inputCalculator = $('input[data-role=p2p-calculator]'),
        $calculatorBuy = $('.calculator-buy'),
        $countInput = $('.count-input');

    let  productId, amount_profit, amount;

    $inputCalculator.on('input', function(){
        calculate.operation($(this))
    });

    $calculatorBuy.on('click', function () {
        productId = $(this).attr('data-productid');
        amount = $countInput.val();
        amount_profit = $("#expected_income").text();
        if (amount % 100 !== 0 || amount == '') {
            return signModel("请输入100的整数倍???？")
        } else {
            window.location.href = `/weixin/view/buy/${productId}/?amount=${amount}`;
        }
    })
})()