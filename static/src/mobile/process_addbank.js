import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName } from './mixins/api'
import { Simple_validation } from './mixins/simple_validation.js'
import { limit} from './mixins/bank_limit.js'

(() => {

    const
        $submit = $('button[type=submit]'),
        $bank = $('select[name=bank]'),
        $bankcard = $('input[name=bankcard]'),
        $bankphone = $('input[name=bankphone]'),
        $validation = $('input[name=validation]'),
        $money = $('input[name=money]');



//---------------初始化操作start---------
    const autolist = [
        {target: $bank, required: true},
        {target: $bankcard, required: true},
        {target: $bankphone, required: true},
        {target: $validation, required: true},
        {target: $money, required: true},
    ];
    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
    });
    auto.operationClear();

    const codeAutoList = [
        {target: $bank, required: true},
        {target: $bankcard, required: true},
        {target: $bankphone, required: true}
    ]
    const code = new Automatic({
        submit: $('.regist-validation'),
        checklist: codeAutoList
    });
//---------------初始化操作end---------

    //验证短信码所需表单
    const checkOperation_validation = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'isEmpty', value: $bank.val()},
                    {type: 'bankCard', value: $bankcard.val()},
                    {type: 'phone', value: $bankphone.val()}
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            signModel(sign);
            return console.log('验证失败');
        })
    }

    //验证表单
    const checkOperation_submit = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'isEmpty', value: $bank.val()},
                    {type: 'bankCard', value: $bankcard.val()},
                    {type: 'phone', value: $bankphone.val()},
                    {type: 'isEmpty', value: $validation.val()}
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            signModel(sign);
            return console.log('验证失败');
        })
    }


     //渲染银行卡
     const appendBanks = (banks) => {
        let str = '';
        for (let bank in banks) {
            str += `<option value ="${banks[bank].gate_id}" >${banks[bank].name}</option>`;
        }
        return str
    }

    //获取银行卡
    const fetch_banklist = (callback) => {
        if(localStorage.getItem('bank')){
            const content = JSON.parse(localStorage.getItem('bank'));
            $bank.append(appendBanks(content));
            return callback && callback(content)

        }else{
            ajax({
                type: 'POST',
                url: '/api/bank/list_new/',
                success (results) {
                    if (results.ret_code === 0) {
                        const content = JSON.stringify(results.banks);
                        $bank.append(appendBanks(results.banks));
                        window.localStorage.setItem('bank', content);
                        return callback && callback(content)

                    } else {
                        return alert(results.message);
                    }
                },
                error (data) {
                    console.log(data)
                }
            })
        }
    }

    fetch_banklist(banklist => {
        limit.getInstance({
            target: $('.limit-bank-item'),
            limit_data: banklist
        })
    })

    const $validation_btn = $('button[name=validation_btn]');

    const simple_validation = new Simple_validation({
        target: $validation_btn,
        VALIDATION_URL: '/api/pay/deposit_new/',
    })



    //短信验证码
    $validation_btn.on('click', function(){

        simple_validation.set_check_list([
            {type: 'isEmpty', value: $bank.val()},
            {type: 'bankCard', value: $bankcard.val()},
            {type: 'phone', value: $bankphone.val()},
        ]);

        simple_validation.set_ajax_data({
            card_no: $bankcard.val(),
            gate_id: $bank.val(),
            phone: $bankphone.val(),
            amount: 0.01
        });
        simple_validation.start()

    });
    //绑卡操作
    $submit.on('click', function(){
        checkOperation_submit()
            .then((result) =>{
                var check_recharge = $(this).attr('data-recharge')
                if(check_recharge == 'true'){
                    confirm("充值金额为" + $money.val(), '确认充值', recharge, {firstRecharge: true});
                }else{
                    recharge({firstRecharge: false})
                }

            })
            .catch(result => {

            })
    })

    function recharge(check){
        org.ajax({
            type: 'POST',
            url: '/api/pay/cnp/dynnum_new/',
            data: {
                phone: $bankphone.val(),
                vcode: $validation.val(),
                order_id: $('input[name=order_id]').val(),
                token: $('input[name=token]').val(),
                set_the_one_card: true
            },
            beforeSend: function () {
                if(check.firstRecharge){
                    $submit.attr('disabled', 'disabled').text('充值中...');
                }else{
                    $submit.attr('disabled', 'disabled').text('绑卡中...');
                }

            },
            success: function (data) {
                if (data.ret_code > 0) {
                    return alert(data.message);
                } else {
                    if(check.firstRecharge){
                        $('.sign-main').css('display', '-webkit-box').find(".balance-sign").text(data.amount);
                    }else{
                        const next_url = getQueryStringByName('next'),
                            next = next_url == '' ? '/weixin/list/' : next_url;
                        return alert('绑卡成功！', ()=>{
                            window.location.href = next
                        });
                    }

                }
            },
            error: function(result){
                var data = JSON.parse(result.responseText);
                return alert(data.detail);
            },
            complete: function () {
                if(check.firstRecharge){
                    $submit.removeAttr('disabled').text('绑卡并充值');
                }else{
                    $submit.removeAttr('disabled').text('立即绑卡');
                }

            }
        })
    }
})();