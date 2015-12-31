import { ui_alert, ui_signError, ui_confirm} from './mixins/ui'
import { Automatic } from './mixins/automatic_detection'
import { ajax } from './mixins/functions'
import { check } from './mixins/check'

(() => {

    const
        $submit = $('button[type=submit]'),
        $username = $('input[name=username]'),
        $idcard = $('input[name=idcard]'),
        autolist = [
            {target: $username, required: true},
            {target: $idcard, required: true},
        ];
//---------------初始化操作start---------

    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
    });
    auto.operation();
//---------------初始化操作end---------


//---------------注册操作start---------

    //验证表单
    const checkOperation = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'isEmpty', value: $username.val()},
                    {type: 'idCard', value: $idcard.val()},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            ui_signError(sign);
            return console.log('验证失败');
        })
    }

    //注册
    function authentication(url) {
        return new Promise((resolve, reject) => {
            ajax({
                url: url,
                type: 'POST',
                data: {
                    'name': $username.val(),
                    'id_number': $idcard.val(),
                },
                beforeSend(){
                    $submit.text('认证中,请稍等...').attr('disabled', 'true');
                },
                success(data){
                    resolve(data)
                },
                error(xhr){
                    reject(xhr)
                },
                complete(){
                    $submit.text('实名认证').removeAttr('disabled');
                }
            });
        });
    }

    $submit.on('click', () => {
        checkOperation()
            .then((result)=> {
                console.log(result); //check success
                return authentication('/api/id_validate/');
            })
            .then((result)=> {
                ui_alert('实名认证成功', ()=> {
                    window.location.href= '/fuel_card/regist/bank/';
                });
            })
            .catch((xhr) => {
                result = JSON.parse(xhr.responseText);
                return ui_signError(result.message);
            })
    });
//---------------注册操作end---------
})();