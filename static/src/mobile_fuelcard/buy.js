import './mixins/ui'
import { ajax, signView } from './mixins/functions'
import { check } from './mixins/check'


(() => {

    const
        $submit = $('button[type=submit]'),
        $reduce = $('.reduce-num'),
        $add = $('.add-num'),
        $count = $('.value-num'),
        balance = $('.fuel-balance').attr('data-balance') * 1,
        $per  = $('.fuel-per'),
        per_value = $per.attr('data-per') * 1;

    class MathCount{
        constructor(count, amount){
            this.count = count;
            this.amount = amount;
            this.style = this.style.bind(this);
        }
        add(){
            this.count += 1;
            this.style()
        }

        reduce(){
            if(this.count <= 1 ) return
            this.count -= 1;
            this.style()
        }

        style(){
            $count.text(this.count);
            $per.text(this.count * this.amount)
            this.count <= 1 ?  $reduce.addClass('num-disabled'): $reduce.removeClass('num-disabled')
        }

    }

    const math = new MathCount(1, per_value);
    $reduce.on('click', () => { math.reduce() });
    $add.on('click', () => { math.add() })

    $submit.on('click', () => {
        if(balance > $per.text()*1) return signView('余额不足！')


    })

})()


