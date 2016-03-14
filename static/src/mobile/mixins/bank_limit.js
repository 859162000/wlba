/**
 * 银行限额
 * @type {{getInstance}}
 *
 */

export const limit = (()=>{

    let _instance = null;

    class Limit{
        constructor({target=null, limit_data = null} = {}){

            [this.target, this.limit_data] = [target, limit_data]

            this._format_limit = this._format_limit.bind(this);
            this.target.html(this._style(this.limit_data))
        }

        _style(limit_data){
            let string_list = ''
            for(let i =0; i< limit_data.length;i++){
                string_list += "<div class='limit-bank-list'>"
                string_list += "<div class='limit-list-dec'>"
                string_list += `<div class='bank-name'>${limit_data[i].name}</div>`;
                string_list += `<div class='bank-limit'>首次限额${this._format_limit(limit_data[i].first_one)}/单笔限额${this._format_limit(limit_data[i].first_one)}/日限额${this._format_limit(limit_data[i].second_day)}</div>`;
                string_list += "</div>"
                string_list += "<div class='limit-list-icon "+limit_data[i].bank_id+"'></div>"
                string_list += "</div>"
            }

            return string_list
        }

        _format_limit(amount){
            let money = amount, reg = /^\d{5,}$/, reg2 = /^\d{4}$/;
            if(reg.test(amount)){
                return money = amount.replace('0000','') + '万'
            }
            if(reg2.test(amount)){
                return money = amount.replace('000','') + '千'
            }
        }
        //
        //show(){
        //    this.target.show()
        //}
        //
        //hide(){
        //    this.target.hide()
        //}
    }

    const getInstance = (data) => {
        if(!_instance){
            _instance = new Limit(data)
        }
        return _instance;
    }

    return {
        getInstance: getInstance
    }

})();
