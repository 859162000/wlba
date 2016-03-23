


export class Trade {
    constructor({header = '交易密码', explain = '充值金额', done = null} = {}) {
        [this.header, this.explain, this.done] = [header, explain, done];

        this.$layout = $('.tran-warp');
        this.$digt = $('.six-digt-password');
        this.$input = null;
        this.password = null;
        this.rectangleWidth = null;
        this.hash = this.hash.bind(this);
        this.createInput = this.createInput.bind(this);
        this.rectangleShow = this.rectangleShow.bind(this);
        this.rectangleHide = this.rectangleHide.bind(this);
        this.layoutHide = this.layoutHide.bind(this);
        this.callback = this.callback.bind(this);
        this.build();
        this.render();

    }

    hash() {
        let hash = Math.random().toString(36).substr(2);
        if ($('#' + hash).length > 0) return this.hash();
        return hash
    }

    createInput() {
        let HASH = this.hash()
        let input_body = `<input type='tel' name=${HASH} id=${HASH} oncontextmenu='return false' value='' onpaste='return false' oncopy='return false' oncut='return false' autocomplete='off'  maxlength='6' minlength='6' />`
        this.$layout.append(input_body)
        this.$input = $('#' + HASH);
    }

    render() {
        const _self = this;
        $('.head-title').html(this.header)
        $('.tran-sign').html(this.explain);

        this.createInput();

        this.$layout.find('.tran-close').one('click', () => {
            _self.layoutHide()
        })

        this.$digt.on('click', (e) =>{
            _self.$input.focus();
            _self.rectangleFixed('click')
            e.stopPropagation();
        })

        this.$input.on('input', () =>{
            _self.rectangleFixed('input')
        });

        $(document).on('click', () =>{
            _self.$digt.find('i').removeClass('active')
            _self.rectangleHide()
        })
    }

    build() {
        this.$input && this.$input.off('input');
        $(document).off('click');
        this.$digt.off('click').find('i').removeClass('active')
        this.$layout.find('.circle').hide()
    }

    destroy() {
        this.$input.val('')
        this.$digt.find('i').removeClass('active')
        $('.six-digt-password i ').find('.circle').hide()
    }

    rectangleFixed(type) {
        const value_num = this.$input.val().length;
        let move_space = this.rectangleWidth * value_num;
        $('.circle').hide();

        for (let i = 0; i < value_num; i++) {
            $('.six-digt-password i ').eq(i).find('.circle').show()
        }

        this.password = this.$input.val();

        this.rectangleShow();

        if (value_num == 6) {
            move_space = this.rectangleWidth * 5;
        }

        this.$layout.find('.blue').animate({
            'translate3d': move_space + "px, 0 , 0"
        }, 0)

        if (value_num == 6) {
            this.$digt.find('i').removeClass('active')
            if (type == 'input') {
                this.rectangleHide();
                this.$input.blur();
                this.callback()
            }
        }

        this.$digt.find('i').eq(value_num).addClass('active').siblings('i').removeClass('active')
    }

    rectangleShow() {
        this.rectangleWidth = Math.floor(this.$layout.find('.blue').width());
        return this.$layout.find('.blue').css('visibility', 'visible')
    }

    rectangleHide() {
        return this.$layout.find('.blue').css('visibility', 'hidden')
    }

    loadingShow() {
        return this.$layout.find('.tran-loading').css('display', '-webkit-box')
    }

    loadingHide() {
        return this.$layout.find('.tran-loading').css('display', 'none')
    }

    layoutShow() {
        return this.$layout.show();
    }

    layoutHide() {
        return this.$layout.hide();
    }

    callback() {
        this.done && this.done({
            password: this.password
        })
    }
}

export const Deal_ui = {
    show_alert (state, callback, state_message) {
        $('.tran-alert-error').show().find('.' + state).show().siblings().hide()
        if (state_message)  $('.tran-alert-error').show().find('.' + state).find('p').html(state_message)
        $('.tran-alert-error').find('.alert-bottom').one('click', function () {
            $('.tran-alert-error').hide()
            callback && callback();
        })
        return
    },
    show_entry (count, callback) {
        $('.tran-alert-entry').show().find('.count_pwd').html(count)
        $('.tran-alert-entry').find('.alert-bottom').one('click', function () {
            $('.tran-alert-entry').hide()
            callback && callback();
        })
        return
    },
    show_lock (left, right, dec, callback) {
        $('.tran-alert-lock').show()
        $('.lock-close').html(left).one('click', function () {
            $('.tran-alert-lock').hide()

        });
        $('.tran-alert-lock').find('.tran-dec-entry').html(dec)
        $('.lock-back').html(right).one('click', function () {
            callback && callback();
        })
    }

}
