import {ui_alert, ui_confirm, ui_signError} from './mixins/ui'
import { ajax } from './mixins/functions'
import { check } from './mixins/check'


(() => {

    const
        $submit = $('button[type=submit]'),
        $reduce = $('.reduce-num'),
        $add = $('.add-num'),
        $count = $('.value-num'),
        balance = $('.fuel-balance').attr('data-balance') * 1,
        $per = $('.fuel-per'),
        per_value = $per.attr('data-per') * 1;

    class MathCount {
        constructor(count, amount) {
            this.count = count;
            this.amount = amount;
            this.count_amount = amount;
            this.style = this.style.bind(this);
        }

        add() {
            this.count += 1;
            this.style()
        }

        reduce() {
            if (this.count <= 1) return
            this.count -= 1;
            this.style()
        }

        get_proerty() {
            return [this.count, this.count_amount]
        }

        style() {
            $count.text(this.count);
            this.count_amount = this.count * this.amount;
            $per.text(this.count * this.amount)
            this.count <= 1 ? $reduce.addClass('num-disabled') : $reduce.removeClass('num-disabled')
        }

    }

    const math = new MathCount(1, per_value);
    const but_operation = (data) => {
        ajax({
            type: 'POST',
            url: '/fuel_card/buy/',
            data: data,
            beforeSend(){
                $submit.attr('disabled', true).html('购买中...')
            },
            success(result){
                return ui_alert(`成功购买加油卡${result.data}元`, function(){
                    const url  = window.location.href;
                    window.location.href = url;
                })
            },
            error(result){
                const data = JSON.parse(result.responseText);
                return ui_signError(data.message)
            },
            complete(){
                $submit.removeAttr('disabled').html('确认购买并支付')
            }

        })
    }

    $reduce.on('click', () => {
        math.reduce()
    });
    $add.on('click', () => {
        math.add()
    })

    $submit.on('click', function () {
        const
            p_id = $(this).attr('data-id'), [p_parts, amount] = math.get_proerty();

        if (balance < amount) return ui_signError('余额不足！')

        const push_data = {
            'p_id': p_id,
            'p_parts': p_parts,
            'amount': amount
        }
        ui_confirm(`购买金额为${amount}` , '确认购买', but_operation, push_data)
    })

})()


