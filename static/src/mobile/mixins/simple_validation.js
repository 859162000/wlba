import { ajax } from './api'
import { signModel } from './ui'
import { check } from './from_validation'

/**
 * 短信验证码按钮封装
 * @param VALIDATION_URL 必填
 * @param target  必填
 * @param validation_form 必填
 * @param callback 选填
 */

export class Simple_validation {
    constructor({target = null,  VALIDATION_URL= null,  callback=null }= {}) {
        [this.target, this.VALIDATION_URL, this.callback ] = [target, VALIDATION_URL, callback];
        this.post_data = null;
        this.check_list = null;
        this.intervalId = null;
        this.before_validation = this.before_validation.bind(this);
        this.timerFunction = this.timerFunction.bind(this);
        this.execute_request = this.execute_request.bind(this)
    }

    set_ajax_data(data_list){
        this.post_data = data_list
    }

    set_check_list(list){
        this.check_list = list
    }

    before_validation() {
        const checklist = this.check_list;

        return new Promise((resolve, reject) => {
            function validation_operation() {
                let form_list = checklist;
                return check(form_list);
            }

            const [isThrough, sign]  = validation_operation();
            if (isThrough) return resolve('验证成功');

            return reject(sign);
        })
    }


    execute_request() {
        const
            $target = this.target,
            VALIDATION_URL = this.VALIDATION_URL,
            post_data =this.post_data,
            intervalId = this.intervalId;

        return new Promise((resolve, reject) => {
            ajax({
                url: VALIDATION_URL,
                type: 'POST',
                data: post_data,
                beforeSend(){
                    $target.attr('disabled', 'disabled').text('发送中..')
                },
                success(data){
                    if (data.ret_code > 0) {
                        clearInterval(intervalId);
                        $target.text('重新获取').removeAttr('disabled').css('background', '#50b143')

                        return reject(data.message);
                    } else {
                        $("input[name='order_id']").val(data.order_id);
                        $("input[name='token']").val(data.token);
                        return resolve('短信已发送，请注意查收！');
                    }
                },
                error(result){
                    clearInterval(intervalId);
                    $target.text('重新获取').removeAttr('disabled').css('background', '#50b143')
                    return reject(result);
                }
            })
        })
    }

    timerFunction(count) {
        var timerInside = function () {
            if (count > 1) {
                count--;
                return this.target.text(`${count}秒后可重发`);
            } else {
                clearInterval(this.intervalId);
                this.target.text('重新获取').removeAttr('disabled');
                return signModel('倒计时失效，请重新获取')
            }
        };
        timerInside();
        return this.intervalId = setInterval(timerInside, 1000);
    }

    start() {
        this.before_validation()
            .then(result => {
                console.log('验证通过')
                return this.execute_request()
            })
            .then(result => {
                signModel(result)
                this.timerFunction(60)
            })
            .catch(result => {
                return signModel(result)
            })
    }
}
