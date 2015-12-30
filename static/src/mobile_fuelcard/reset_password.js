import { ui_alert, ui_signError } from './mixins/ui'
import { Automatic } from './mixins/automatic_detection'
import { ajax } from './mixins/functions'
import { check } from './mixins/check'

(() => {

    const
        $submit = $('button[type=submit]'),
        $oldPassword = $('input[name=old-password]'),
        $newPassword1 = $('input[name=new-password1]'),
        $newPassword2 = $('input[name=new-password2]'),
        autolist = [
            {target: $oldPassword, required: true},
            {target: $newPassword1, required: true},
            {target: $newPassword2, required: true}
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
                    {type: 'isEmpty', value: $oldPassword.val()},
                    {type: 'password', value: $newPassword1.val()},
                    {type: 'rePassword', value: {
                        psw: $newPassword1.val(),
                        repeatPsw: $newPassword2.val(),
                    }},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            ui_signError(sign);
            return console.log('验证失败');
        })
    }

    //修改密码
    function reset_password(url) {
        ajax({
            url: url,
            type: 'POST',
            data: {
                'old_password': $oldPassword.val(),
                'new_password1': $newPassword1.val(),
                'new_password2': $newPassword2.val(),
            },
            beforeSend(){
                $submit.text('修改中,请稍等...').attr('disabled', 'true');
            },
            success(data){
                ui_alert('密码修改成功，请重新登录', function() {
                    window.location.href= '/fuel_card/login/';
                });
            },
            error(xhr){
                ui_signError('系统出错，请稍后再试');
            },
            complete(){
                $submit.text('修改登录密码').removeAttr('disabled');
            }
        });
    }

    $submit.on('click', () => {
        checkOperation()
            .then((result)=> {
                console.log(result); //check success
                return reset_password('/accounts/password/change/');
            })
            .catch((xhr) => {
                return ui_signError('系统出错，请稍后再试');
            })
    });
//---------------注册操作end---------
})();