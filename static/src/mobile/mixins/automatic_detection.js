/**
 * 表单自动检测
 */
export class Automatic {

    constructor({submit = null, checklist = [], otherlist = []} = {}) {

        [this.submit, this.otherlist, this.checklist] = [submit, otherlist, checklist];

        this.allCheck = this.allRequire();
        this.canSubmit = this.canSubmit.bind(this);
        this.isEmptyString = this.isEmptyString.bind(this);
        this.isEmptyArray = this.isEmptyArray.bind(this);
        this.check();
    }

    allRequire(){
        const allCheck = [...this.checklist, ...this.otherlist];
        return allCheck.filter((target) => {
            if(target.required) return true;
            return false
        })
    }

    isEmptyArray(array) {
        if(array.length === 0) return true;
        return false
    }

    isEmptyString(str) {
        if(str == '') return true;
        return false
    }

    check() {
        if (this.isEmptyArray(this.checklist))
            return console.log('checklist is none');

        const _self = this;
        this.checklist.forEach((dom) => {
            dom.target.on('input', function () {
                _self.style(dom.target);
                _self.canSubmit();
            })
        });
    }

    style(target) {

        const isEmpty = this.isEmptyString(target.val()),
            icon = target.attr('data-icon'),
            othericon = target.attr('data-other'),
            operation = target.attr('data-operation');

        //等于空
        if (isEmpty) {
            if (icon != '') target.siblings(`.${icon}`).removeClass('active');
            if (othericon != '') $(`.${othericon}`).attr('disabled', 'true');
            if (operation != '') target.siblings(`.${operation}`).hide();
        }

        //不等于空
        if (!isEmpty) {
            if (icon != '') target.siblings(`.${icon}`).addClass('active');
            if (othericon != '') $(`.${othericon}`).removeAttr('disabled');
            if (operation != '') target.siblings(`.${operation}`).show();

        }

    }

    canSubmit() {
        const type = 'text|tel|password|select|';
        const _self = this;

        let state = this.allCheck.every((dom) => {
            const target = dom.target;

            if (type.indexOf(target.attr('type')) >= 0) {
                if (_self.isEmptyString(target.val())) {
                    return false
                }
                return true
            }

            if (type.indexOf(dom.target) < 0) {
                if (target.attr('type') == 'checkbox' && target.prop('checked')) {
                    return true
                }
                if(dom.target.length == 0){
                    return true
                }
                return false
            }
        });

        state ? this.submit.removeAttr('disabled') : this.submit.attr('disabled', 'true');
    }

    operationClear() {
        $('.wx-clear-input').on('click', function () {
            $(this).siblings('input').val('').trigger('input');
        })
    }

    operationPassword() {
        $('.wx-password-operation').on('click', function () {
            const type = $(this).siblings('input').attr('type');
            if(type == 'text'){
                $(this).siblings().attr('type', 'password');
                $(this).addClass('wx-hide-password').removeClass('wx-show-password');
            }
            if(type == 'password'){
                $(this).siblings().attr('type', 'text');
                $(this).addClass('wx-show-password').removeClass('wx-hide-password');
            }
        })
    }
}


