import { ajax } from './api'
import { signModel } from './ui'
import { check } from './from_validation'

export const validation = ($phone, $captcha_0, $captcha_1, $captcha) => {

    let intervalId = null;
    const $validate_operation = $('button[name=validate_operation]');

    //获取图像验证码
    function validation() {
        var url = '/captcha/refresh/?v=' + new Date().getTime();
        $.get(url, function (result) {
            $captcha.attr('src', result['image_url']);
            $captcha_0.val(result['key']);
        });
    }

    validation();

    //验证表单
    const checkOperation = (phone) => {
        return new Promise((resolve, reject) => {
            function checkOperation() {
                const checklist = [
                    {type: 'phone', value: phone},
                ];
                return check(checklist);
            }

            const [isThrough, sign]  = checkOperation();
            if (isThrough) return resolve('验证成功');

            return reject(sign);
        })
    }

    //获取短信验证码
    function fetchValidation(phone, captcha_0, captcha_1) {
        return new Promise((resolve, reject)=> {
            ajax({
                url: `/api/phone_validation_code/${phone}/`,
                data: {
                    captcha_0: captcha_0,
                    captcha_1: captcha_1,
                },
                type: 'POST',
                beforeSend(){
                    $validate_operation.attr('disabled', 'disabled').text('发送中..')
                },
                success(){
                    resolve('短信已发送，请注意查收！');
                },
                error: function (xhr) {
                    var result = JSON.parse(xhr.responseText);
                    $validate_operation.removeAttr('disabled').text('获取验证码');
                    clearInterval(intervalId);
                    validation();
                    return reject(result.message);
                }
            });
        })
    }

    //倒计时
    function timerFunction(count) {
        return new Promise((resolve, reject)=> {
            var timerFunction = function () {
                if (count > 1) {
                    count--;
                    return $validate_operation.text(`${count}秒后可重发`);
                } else {
                    clearInterval(intervalId);
                    $validate_operation.text('重新获取').removeAttr('disabled');
                    validation();
                    return reject('倒计时失效，请重新获取')
                }
            };
            timerFunction();
            return intervalId = setInterval(timerFunction, 1000);
        })
    }

    //图像验证码
    $captcha.on('click', () => {
        validation()
    });

    //短信验证码
    $validate_operation.on('click', function () {
        const phone = $phone.val(),
            captcha_0 = $captcha_0.val(),
            captcha_1 = $captcha_1.val();

        chained(phone, captcha_0, captcha_1)
    });

    function chained(phone, captcha_0, captcha_1) {
        /**
         * 所有的逻辑在这里，获取短信验证码的时候，先检查手机号是否符合，
         * 成功后 fetchValidation（发送短信请求）
         * 成功后 timerFunction（倒计时）
         */
        checkOperation(phone)
            .then(()=> {
                console.log('验证成功')
                return fetchValidation(phone, captcha_0, captcha_1)
            })
            .then((message)=> {
                signView(message)
                console.log('短信发送成功');
                let count = 60;
                return timerFunction(count)
            })
            .catch((message)=> {
                signView(message)
            })
    }


}