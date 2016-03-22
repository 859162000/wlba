import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName } from './mixins/api'
import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import 'polyfill'

(() => {

    const
        $submit = $('button[type=submit]'),
        $name = $('input[name=name]'),
        $idcard = $('input[name=idcard]');

//---------------初始化操作start---------
    const autolist = [
        {target: $name, required: true},
        {target: $idcard, required: true}
    ];
    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
    });
    auto.operationClear();
//---------------初始化操作end---------


//---------------login操作start---------

    //验证表单
    const checkOperation = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'isEmpty', value: $name.val()},
                    {type: 'idCard', value: $idcard.val()},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            signModel(sign);
            return console.log('验证失败');
        })
    }
    //认证
    const authentication = (url , postdata) => {
        return new Promise((resolve, reject) => {
            ajax({
                type: 'POST',
                url: url,
                data: postdata,
                beforeSend () {
                    $submit.attr('disabled', true).text("认证中，请等待...");
                },
                success (result) {
                    resolve(result)
                },
                error (xhr) {
                    reject(xhr)
                },
                complete () {
                    $submit.removeAttr('disabled').text("实名认证");
                }
            })
        })

    }

    $submit.on('click', () => {
        checkOperation()
            .then((result)=> {
                console.log(result); //check success
                return authentication('/api/id_validate/', {
                    name: $name.val(),
                    id_number: $idcard.val()
                });
            })
            .then((result)=> {
                console.log('success');
                if (!result.validate == 'true') return alert('认证失败，请重试');
                alert("实名认证成功!", function () {
                    return window.location.href = '/weixin/regist/second/';
                });
            })
            .catch((xhr) => {
                const result = JSON.parse(xhr.responseText);
                if(result.error_number == 8){
                    alert(result.message,function(){
                       window.location.href = '/weixin/list/';
                    });
                }else{
                    return alert(result.message);
                }
            })
    });
//---------------login操作end---------
})();