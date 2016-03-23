import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName } from './mixins/api'
import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'

(() => {

    const
        $submit = $('button[type=submit]'),
        $identifier = $('input[name=identifier]'),
        $password = $('input[name=password]');

    const autolist = [
        {target: $identifier, required: true},
        {target: $password, required: true}
    ];
    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
    });
    auto.operationClear();
    auto.operationPassword();


//---------------login操作start---------

    //验证表单
    const checkOperation = () => {
        return new Promise((resolve, reject) => {
            alert("check");
            function checkOperation() {
                const checklist = [
                    {type: 'phone', value: $identifier.val()},
                    {type: 'password', value: $password.val()},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            signModel(sign);
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
        alert(3);
        checkOperation()
            .then((result)=> {
                console.log(result); //check success
                return login('/weixin/api/login/');
            })
            .then((result)=> {
                console.log('login success');
                const next_url = getQueryStringByName('next');
                window.location.href = next_url ? decodeURIComponent(decodeURIComponent(next_url)) : '/weixin/account/';
            })
            .catch((res) => {
                if (res['status'] == 403) {
                    signModel('请勿重复提交');
                    return false;
                }
                let data = JSON.parse(res.responseText);
                for (let key in data) {
                    data['__all__'] ? signModel(data['__all__'][0]) : signModel(data[key][0]);
                }
            })
    });
//---------------login操作end---------
})();