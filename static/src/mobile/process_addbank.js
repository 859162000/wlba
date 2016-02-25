import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName } from './mixins/api'

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
        {target: $money, required: true}
    ];
    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
    });

    const codeautolist = [
        {target: $bank, required: true},
        {target: $bankcard, required: true},
        {target: $bankphone, required: true}
    ]
    const code = new Automatic({
        submit: $('.regist-validation'),
        checklist: codeautolist
    });
//---------------初始化操作end---------

    //验证表单
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
})();