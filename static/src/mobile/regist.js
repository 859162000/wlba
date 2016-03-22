import { Automatic } from './mixins/automatic_detection'
import { ajax, getQueryStringByName } from './mixins/api'
import { signModel } from './mixins/ui'
import { check } from './mixins/from_validation'
import { validation } from './mixins/images_validation'

(() => {

    const
        $submit = $('button[type=submit]'),
        $identifier = $('input[name=identifier]'),
        $captcha_1 = $('input[name=captcha_1]'),
        $captcha_0 = $('input[name=captcha_0]'),
        $validate_code = $('input[name=validate_code]'),
        $password = $('input[name=password]'),
        $invite_code = $('input[name=invite_code]'),
        $agreement = $('input[name=agreement]'),
        $captcha = $('#captcha');

//---------------初始化操作start---------
    const autolist = [
            {target: $identifier, required: true},
            {target: $captcha_1, required: true},
            {target: $validate_code, required: true},
            {target: $password, required: true},
            {target: $invite_code, required: false}
        ];
    //自动检查
    const auto = new Automatic({
        submit: $submit,
        checklist: autolist,
        otherlist: [
            {target: $agreement, required: true}
        ]
    });
    auto.operationClear();
    auto.operationPassword();
//---------------初始化操作end---------

    //短信验证码
    validation($identifier, $captcha_0, $captcha_1, $captcha)

//---------------注册操作start---------
    //用户协议
    $("#agreement").on('click', function () {
        $(this).toggleClass('agreement');
        $(this).hasClass('agreement') ? $agreement.attr('checked', 'checked') : $agreement.removeAttr('checked');
        $identifier.trigger('input');
    });
    //显示协议
    const $showXiyi = $('.xieyi-btn'),$cancelXiyi = $('.cancel-xiyie'), $protocolDiv = $('.regist-protocol-div');
    $showXiyi.on('click', function (event) {
        event.preventDefault();
        $protocolDiv.css('display', 'block');
        setTimeout(function () {
            $protocolDiv.css('top', '0%');
        }, 0)
    })
    //关闭协议
    $cancelXiyi.on('click', function () {
        $protocolDiv.css('top', '100%');
        setTimeout(function () {
            $protocolDiv.css('display', 'none');
        }, 200)
    })


    //验证表单
    const checkOperation = () => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'phone', value: $identifier.val()},
                    {type: 'isEmpty', value: $captcha_1.val()},
                    {type: 'isEmpty', value: $validate_code.val()},
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

    //注册
    function register(url) {
        return new Promise((resolve, reject) => {
            ajax({
                url: url,
                type: 'POST',
                data: {
                    'identifier': $identifier.val(),
                    'password': $password.val(),
                    'captcha_0': $captcha_0.val(),
                    'captcha_1': $captcha_1.val(),
                    'validate_code': $validate_code.val(),
                    'invite_code': 'weixin',
                    'invite_phone': ''
                },
                beforeSend(){
                    $submit.text('注册中,请稍等...').attr('disabled', 'true');
                },
                success(data){
                    resolve(data)
                },
                error(xhr){
                    reject(xhr)
                },
                complete(){
                    $submit.text('立即注册 ｜ 领取奖励').removeAttr('disabled');
                }
            });
        });
    }

    $submit.on('click', () => {
        checkOperation()
            .then((result)=> {
                console.log(result); //check success
                return register('/api/register/');
            })
            .then((result)=> {
                console.log('register success');
                if (result.ret_code === 0) {
                    alert('注册成功', ()=> {
                        var next = getQueryStringByName('next') == '' ? '/weixin/regist/first/' : getQueryStringByName('next');
                            next = getQueryStringByName('mobile') == '' ? next : next + '&mobile='+ getQueryStringByName('mobile');
                            next = getQueryStringByName('serverId') == '' ? next : next + '&serverId='+ getQueryStringByName('serverId');
                        window.location.href = next;
                    });
                }
                if (result.ret_code > 0) {
                    signModel(result.message)
                }
            })
            .catch((xhr) => {
                var result = JSON.parse(xhr.responseText);
                if (xhr.status === 429) {
                    signModel('系统繁忙，请稍候重试')
                } else {
                    signModel(result.message);
                }
            })
    });
//---------------注册操作end---------
})();