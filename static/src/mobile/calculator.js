import { calculate  } from './mixins/api'
import { signModel } from './mixins/ui.js'

(() => {


   calculate($('input[data-role=p2p-calculator]'))

    const
        $calculatorBuy = $('.calculator-buy'),
        $countInput = $('.count-input');
    var
        productId, amount_profit, amount;

    $calculatorBuy.on('click', function () {
        productId = $(this).attr('data-productid');
        amount = $countInput.val();
        amount_profit = $("#expected_income").text();
        if (amount % 100 !== 0 || amount == '') {
            return alert("请输入100的整数倍")
        } else {
            window.location.href = `/weixin/view/buy/${productId}/?amount=${amount}&amount_profit=${amount_profit}`;
        }
    })
})()