import { ui_alert, ui_signError, ui_confirm} from './mixins/ui'
import { Automatic } from './mixins/automatic_detection'
import { ajax } from './mixins/functions'
import { check } from './mixins/check'
import { validation } from './mixins/validation'

(() => {

    const
        $submit = $('button[type=submit]'),
        $bank = $('select[name=bank]'),
        $bankcard = $('input[name=bankcard]'),
        $bankphone = $('input[name=bankphone]'),
        $validation = $('input[name=validation]'),
        $validate_operation = $('button[name=validate_operation]'),

        autolist = [
            {target: $bank, required: true},
            {target: $bankcard, required: true},
            {target: $bankphone, required: true},
            {target: $validation, required: true},
        ];
//---------------初始化操作start---------
    //获取银行卡列表
    ~function () {
        if (localStorage.getItem('bank')) {
            const content = JSON.parse(localStorage.getItem('bank'));
            _appendLimit(content)
            return $bank.append(_appendBanks(content));
        }
        ajax({
            type: 'POST',
            url: '/api/bank/list_new/',
            success: function (results) {
                if (results.ret_code === 0) {
                    const content = JSON.stringify(results.banks);
                    _appendLimit(content)
                    $bank.append(_appendBanks(results.banks));
                    window.localStorage.setItem('bank', content);
                } else {
                    return ui_signError(results.message);
                }
            },
            error: function (data) {
                console.log(data)
            }
        })

        function _format_limit(amount) {
            const reg = /^\d{5,}$/, reg2 = /^\d{4}$/;
            if (reg.test(amount)) {
                return `${amount.replace('0000', '')}万`
            }
            if (reg2.test(amount)) {
                return `${amount.replace('000', '')}千`
            }
        }

        function _appendLimit(data) {
            const $limitItem = $('.limit-bank-item');
            let list = '';
            for (let i = 0; i < data.length; i++) {
                list += `
                        <div class='limit-bank-list'>
                            <div class='limit-list-dec'>
                                <div class='bank-name'>${data[i].name}</div>
                                <div class='bank-limit'>首次限额${_format_limit(data[i].first_one)}/单笔限额${_format_limit(data[i].first_one)}/日限额${_format_limit(data[i].second_day)}</div>
                            </div>
                            <div class='limit-list-icon ${data[i].bank_id}'></div>
                        </div>`;
            }
            $limitItem.html(list)
        }

        function _appendBanks(banks) {
            let str = '';
            for (let bank in banks) {
                str += `<option value = '${banks[bank].gate_id}' >${banks[bank].name}</option>`;
            }
            return str
        }
    }()


    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
    });
    auto.operation();

    $('select[name=bank]').change(function () {
        const icon = $(this).attr('data-icon');
        if ($(this).val() == '') {
            $(this).siblings(`.${icon}`).removeClass('active');
        } else {
            $(this).siblings(`.${icon}`).addClass('active');
        }
        $('input[name=password]').trigger('input')
    });


//---------------初始化操作end---------

//短信验证码
    //验证表单
    const checkOperation_bank = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'isEmpty', value: $bank.val()},
                    {type: 'bankCard', value: $bankcard.val()},
                    {type: 'phone', value: $bankphone.val()},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            ui_signError(sign);
            return console.log('验证失败');
        })
    }

    const get_validation = (url) => {
        return new Promise((resolve, reject) => {
            ajax({
                url: url,
                type: 'POST',
                data: {
                    'card_no': $bankcard.val(),
                    'amount': 0.01,
                    'phone': $bankphone.val(),
                    'gate_id': $bank.val()
                },
                beforeSend(){
                    $validate_operation.attr('disabled', 'disabled').text('发送中..');
                },
                success(results){
                    if (results.ret_code === 0) {
                        ui_signError('短信已发送，请注意查收！')
                        $("input[name='order_id']").val(results.order_id);
                        $("input[name='token']").val(results.token);
                        return resolve('短信已发送，请注意查收！');
                    }

                    if (results.ret_code > 0) {
                        ui_signError(results.message)
                        return reject('获取短信验证码错误');
                    }

                },
                error(xhr){
                    reject(xhr)
                },
                complete(){
                    $validate_operation.removeAttr('disabled').text('获取验证码');
                }
            });
        });
    }

    //倒计时
    const timerFunction = (count) => {
        return new Promise((resolve, reject)=> {
            var timerFunction = function () {
                if (count > 1) {
                    count--;
                    return $validate_operation.text(`${count}秒后可重发`);
                } else {
                    clearInterval(intervalId);
                    $validate_operation.text('重新获取').removeAttr('disabled');
                    ui_signError('倒计时失效，请重新获取')
                    return reject('倒计时失效，请重新获取')
                }
            };
            timerFunction();
            return intervalId = setInterval(timerFunction, 1000);
        })
    }

    $validate_operation.on('click', () => {
        checkOperation_bank()
            .then((result)=> {
                console.log(result);
                return get_validation('/api/pay/deposit_new/');
            })
            .then((result)=> {
                console.log('短信发送成功，自信倒计时');
                const count = 60;
                return timerFunction(count)
            })
            .catch((message) => {
                console.log(message)
            })
    });

//---------------绑卡操作start---------

    //验证表单
    const checkOperation = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'isEmpty', value: $bank.val()},
                    {type: 'bankCard', value: $bankcard.val()},
                    {type: 'phone', value: $bankphone.val()},
                    {type: 'isEmpty', value: $validation.val()},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            ui_signError(sign);
            return console.log('验证失败');
        })
    }

    //绑卡
    function set_bank(url) {
        return new Promise((resolve, reject) => {
            ajax({
                url: url,
                type: 'POST',
                data: {
                    phone: $bankphone.val(),
                    vcode: $validation.val(),
                    order_id: $('input[name=order_id]').val(),
                    token: $('input[name=token]').val(),
                    set_the_one_card: true
                },
                beforeSend(){
                    $submit.text('绑定中,请稍等...').attr('disabled', 'true');
                },
                success(data){
                    if (data.ret_code > 0) {
                        reject(data.message)
                        return ui_signError(data.message);
                    } else {
                        return ui_alert('恭喜你，绑卡成功！', () => {
                            resolve(data.message)
                            window.location.href = '/fuel_card/regist/end/';
                        });
                    }

                },
                error(xhr){
                    reject(xhr)
                },
                complete(){
                    $submit.text('绑定银行卡').removeAttr('disabled');
                }
            });
        });
    }

    $submit.on('click', () => {
        checkOperation()
            .then((result)=> {
                console.log(result); //check success
                return set_bank('/api/pay/cnp/dynnum_new/');
            })
            .then((result)=> {
                console.log(result)
            })
            .catch((xhr) => {
                console.log(result)
            })
    });
//---------------绑卡操作end---------
})();