
export const check = (checklist) => {
    let [result, error] = [null, null];

    $.each(checklist, (index,target) => {

        [result, error] = validation[target.type](target.value);

        if (!result) return false
    });

    return [result, error]
};


const validation = {
    phone(str){
        const phone = parseInt($.trim(str)),
            error = '请输入正确的手机号',
            re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);

        if (re.test(phone)) {
            return [true, '']
        }
        return [false, error]
    },
    password(str){
        const error = '密码为6-20位数字/字母/符号/区分大小写',
            re = new RegExp(/^\d{6,20}$/);
        if (re.test($.trim(str))) {
            return [true, '']
        }
        return [false, error]
    },
    rePassword({psw= null, repeatPsw=null} = {}){
        const error = '两次密码不相同';
        if (psw !== repeatPsw) {
            return [false, error]
        }
        return [true, '']
    },
    tranPassword(str){
        const error = '交易密码为6位数字',
            re = new RegExp(/^\d{6}$/);
        if (re.test($.trim(str)) && !isNaN($.trim(str))) {
            return [true, '']
        }
        return [false, error]
    },
    idCard(str){
        const error = '银行卡号不正确',
            re = new RegExp(/^\d{12,20}$/);
        if (re.test($.trim(str)) && !isNaN($.trim(str))) {
            return [true, '']
        }
        return [false, error]
    },
    bankCard(str){
        const error = '身份证号不正确',
            re = new RegExp(/^.{15,18}$/);
        if (re.test($.trim(str)) && !isNaN($.trim(str))) {
            return [true, '']
        }
        return [false, error]
    },
    money100(str){
        const error = '请输入100的倍数金额';
        if (str % 100 === 0) {
            return [true, '']
        }
        return [false, error]
    },
    isEmpty(str){
        const error = '请填写全部的表单';
        if (str === '') {
            return [false, error]
        }
        return [true, '']
    },
};