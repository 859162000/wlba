import { ui_alert, ui_signError} from './mixins/ui'
import { Automatic } from './mixins/automatic_detection'
import { ajax } from './mixins/functions'
import { check } from './mixins/check'

(() => {

    const
        $submit = $('button[type=submit]'),
        $identifier = $('input[name=identifier]'),
        $password = $('input[name=password]'),
        autolist = [
            {target: $identifier, required: true},
            {target: $password, required: true},
        ];
//---------------初始化操作start---------

    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
    });
    auto.operation();
    auto.operationPassword();
//---------------初始化操作end---------


//---------------login操作start---------

    //验证表单
    const checkOperation = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'phone', value: $identifier.val()},
                    {type: 'password', value: $password.val()},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            ui_signError(sign);
            return console.log('验证失败');
        })
    }

    //登录
    function login(url) {
        return new Promise((resolve, reject) => {
            ajax({
                url: url,
                type: 'POST',
                data: {
                    'identifier': $identifier.val(),
                    'password': $password.val(),
                },
                beforeSend(){
                    $submit.text('登录中,请稍等...').attr('disabled', 'true');
                },
                success(data){
                    resolve(data)
                },
                error(res){
                    reject(res)
                },
                complete(){
                    $submit.text('登录网利宝').removeAttr('disabled');
                }
            });
        });
    }

    $submit.on('click', () => {
        checkOperation()
            .then((result)=> {
                console.log(result); //check success
                return login('/weixin/api/login/');
            })
            .then((result)=> {
                console.log('login success');
                window.location.href = '/fuel_card/index/';
            })
            .catch((res) => {
                if (res['status'] == 403) {
                    ui_signError('请勿重复提交')
                    return false;
                }
                let data = JSON.parse(res.responseText);
                for (let key in data) {
                    data['__all__'] ?  ui_signError(data['__all__'][0]) : ui_signError(data[key][0]);
                }
            })
    });
//---------------login操作end---------
})();