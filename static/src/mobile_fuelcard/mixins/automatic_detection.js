
export class Automatic {

    constructor({submit = null, checklist = [], otherlist = []} = {}) {

        [this.submit, this.otherlist, this.checklist] = [submit, otherlist, checklist];

        this.allCheck = [...checklist, ...otherlist];

        this.check = this.check.bind(this);
        this.canSubmit = this.canSubmit.bind(this);
        this.isEmptyString = this.isEmptyString.bind(this);
        this.isEmptyArray = this.isEmptyArray.bind(this);
    }

    isEmptyArray(array){
        if(array.length === 0) return true;
        return false
    }

    isEmptyString(string) {

        if(string == '') return true;
        return false
    }

    check(){
        if(this.isEmptyArray(this.checklist))
            return console.log('checklist is none');

        this.checklist.forEach((dom) => {
            console.log(this.allCheck)
            const _self = this;
            dom.target.on('input', function(){
                _self.style(dom.target);
                _self.canSubmit();
            })
        });
    }

    style(target){

        const isEmpty = this.isEmptyString(target.val()),
            icon = target.attr('data-icon'),
            operation = target.attr('data-operation');

        //等于空
        if(isEmpty){
            if(icon != '') target.siblings(`.${icon}`).removeClass('active');
            if(operation != '') target.siblings(`.${operation}`).hide();
        }

        //不等于空
        if(!isEmpty){
            if(icon != '') target.siblings(`.${icon}`).addClass('active')
            if(operation != '') target.siblings(`.${operation}`).show();
        }

    }

    canSubmit(){

    }

}


