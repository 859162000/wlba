CanvasRenderingContext2D.prototype.clear = function () {
    this.save();
    this.globalCompositeOperation = 'destination-out';
    this.fillStyle = 'black';
    this.fill();
    this.restore();
};
CanvasRenderingContext2D.prototype.clearArc = function (x, y, radius, startAngle, endAngle, anticlockwise) {
    this.beginPath();
    this.arc(x, y, radius, startAngle, endAngle, anticlockwise);
    this.clear();
};

org.finance = (function (org) {
    var lib = {
        process_num: 0,
        model_canvac_opeartion: true,
        canvas_model4: null,
        init: function () {

            lib.fetch_data();
            lib.listen_handle()
        },
        listen_handle: function(){
            $('.finance-mode-btnl-aue').on('click', function(){
                $('.client-share-model').show()
            })
            $('.client-share-model').on('click', function(){
                $(this).hide()
            })

        },
        swiper_init: function(rm_page){

            var swiper = new Swiper('.swiper-container', {
                direction: 'vertical',
                initialSlide: 0,
                onSlideChangeEnd: function (swiper) {

                    if (swiper.activeIndex == 2) {
                        var canvas_model3_data = $('.tz_max_ranking_percent').text() * 1;
                        lib.canvas_model3_doging(canvas_model3_data)
                    }
                    if (swiper.activeIndex == 3) {
                        if (!lib.canvas_model4) {
                            var sort = $('.tz_sterm_percent').text() * 1;
                            var mid = $('.tz_mterm_percent').text() * 1;
                            var long = $('.tz_lterm_percent').text() * 1;
                            lib.cavas_model4(sort, mid, long)
                        }

                    }
                }
            });

            swiper.removeSlide(rm_page);
            swiper.update(true)
            $('.refresh').html($('.swiper-slide').length)


        },
        fetch_data: function () {
            var _self = this;
            org.ajax({
                url: '/api/account2015/',
                type: 'post',
                success: function (result) {
                    if (result.error_code == 0) {
                        var account = result.account;
                        //判断用户类型
                        if(parseInt(account.tz_amount) > 0){
                            _self.swiper_init([6])
                        }

                        if(parseInt(account.tz_amount) <= 0 && parseInt(account.income_reward) > 0){
                            _self.swiper_init([1,2,3,6])
                        }

                        if(parseInt(account.tz_amount) <= 0 && parseInt(account.income_reward) <= 0){
                            _self.swiper_init([1,2,3,4,5])
                        }

                        //page1
                        $('.zc_ranking').text(account.zc_ranking)
                        $('.tz_amount').text( '￥'+ account.tz_amount)
                        $('.tz_ranking_percent').text(account.tz_ranking_percent)
                        $('.income_total').text('￥'+ account.income_total)
                        //page2
                        $('.user-name').text('亲爱的'+ account.user_name)
                        $('.tz_times').text(account.tz_times)
                        $('.tz_avg_times').text(account.tz_avg_time)
                        $('.tz_max_amount').text(account.tz_max_amount)
                        $('.tz_max_ranking_percent').text(Math.floor(account.tz_max_ranking_percent))
                        //page3
                        $('.tz_sterm_percent').text(account.tz_sterm_percent)
                        $('.tz_mterm_percent').text(account.tz_mterm_percent)
                        $('.tz_lterm_percent').text(account.tz_lterm_percent)
                        var name = _self.set_limit_style(account.tz_sterm_percent, account.tz_mterm_percent, account.tz_lterm_percent)
                        $('.model4-head-name').text(name)
                        //page4
                        $('.invite_count').text(account.tz_sterm_point)
                        $('.invite_income').text(account.tz_mterm_point)
                        var message = _self.set_invite_count_style(account.tz_lterm_point)
                        $('.cravat-cue-detail').text(message.name)
                        $('.cravat-alert').text(message.detail)
                        //page5
                        $('.income_reward').text(account.income_reward)
                        $('.income_hb_expire').text(account.income_hb_expire)
                        $('.income_jxq_expire').text(account.income_jxq_expire)
                        var sheep_count = _self.set_sheep_style(account.income_reward)
                        for (var i = 0; i < sheep_count; i++) {
                            $('.model6-yang-icon').append("<div class='sheep-icon'></div>")
                        }
                        var chinese_num = ['一', '二', '三', '四', '五']
                        $('.sheep-account').text(chinese_num[sheep_count - 1] + '只羊')

                        $('.client-loding-warp').animate({
                            opacity: 0
                        }, 300, function () {
                            $(this).hide()
                        })

                    }
                }

            })
        },
        set_limit_style: function (sort, mid, long) {
            if (long >= sort && long >= mid) {
                return '最爱：长期优选'
            }
            if (mid >= sort && mid > long) {
                return '最爱：中期稳健'
            }
            if (sort > mid && sort > long) {
                return '最爱：短期灵活'
            }
        },
        set_invite_count_style: function (count) {
            var
                name = ['茕茕孑立', '门可罗雀', '门庭若市'],
                detail = ['孤身一人，一个全民淘金好友都没邀请到。', '全民淘金所邀请好友数稀少。', '全民淘金邀请到的好友很多热闹得像人才市场一样。']
            if (count == 0) {
                return {
                    name: name[0],
                    detail: detail[0]
                }
            }
            if (count >= 1 && count <= 10) {
                return {
                    name: name[1],
                    detail: detail[1]
                }
            }

            if (count >= 10) {
                return {
                    name: name[2],
                    detail: detail[2]
                }
            }

        },
        set_sheep_style: function (amount) {
            if (amount <= 100) return 1;
            if (amount > 100 && amount <= 500) return 2;
            if (amount > 500 && amount <= 5000) return 3;
            if (amount > 500 && amount <= 5000) return 4;
            if (amount > 50000) return 5
        },
        canvas_model3_doging: function (percent) {
            var _self = this, canvas_w = 140, canvas_r = 140, canvas_font = '34px';
            var isAndroid = navigator.userAgent.indexOf('Android') > -1 || navigator.userAgent.indexOf('Adr') > -1; //android终端
            if (isAndroid) {
                canvas_w = canvas_w / 2
                canvas_r = canvas_r / 2
                canvas_font = '17px'
            }
            function infinite() {
                _self.canvas_model3(canvas_w / 2, canvas_w / 2, canvas_r / 2, _self.process_num, canvas_w, canvas_font);
                t = setTimeout(infinite, 30);

                if (_self.process_num >= percent) {
                    clearTimeout(t);
                    _self.process_num = 0;
                    return;
                }
                _self.process_num += 1;
            }

            infinite()
        },
        canvas_model3: function (x, y, radius, process, canvas_w, canvas_font) {
            var _self = this;
            var canvas = document.getElementById('canvas-model3');

            if (canvas.getContext) {
                var cts = canvas.getContext('2d');

                if (_self.model_canvac_opeartion) {
                    canvas.getContext('2d').translate(0.5, 0.5)
                    canvas.width = canvas_w;
                    canvas.height = canvas_w;
                    _self.model_canvac_opeartion = false
                }
            } else {
                return;
            }

            cts.beginPath();
            cts.moveTo(x, y);
            cts.arc(x, y, radius, 0, Math.PI * 2, false);
            cts.closePath();
            cts.fillStyle = '#D8D8D8';
            cts.fill();

            cts.beginPath();
            cts.moveTo(x, y);
            endAgl = Math.PI * 2 * process / 100
            cts.arc(x, y, radius, 0, endAgl, false);
            cts.closePath();
            cts.fillStyle = '#FDF11C';
            cts.fill();
            cts.clearArc(x, y, radius - (radius * 0.26), 0, Math.PI * 2, true);
            //在中间写字
            cts.font = canvas_font + ' Arial'
            cts.fillStyle = '#FDF11C';
            cts.textAlign = 'center';
            cts.textBaseline = 'middle';
            cts.moveTo(x, y);
            cts.fillText(process + "%", x, y);
        },
        cavas_model4: function (sort, mid, long) {
            var doughnutData = [
                {
                    value: sort,
                    color: "#4877C8"
                },
                {
                    value: mid,
                    color: "#FFBA26"
                },
                {
                    value: long,
                    color: "#F35B47"
                },

            ];
            var canvas_target = document.getElementById("model4-canvas");
            var _self = this, canvas_w = 300, canvas_h = 300
            var isAndroid = navigator.userAgent.indexOf('Android') > -1 || navigator.userAgent.indexOf('Adr') > -1; //android终端
            if (isAndroid) {
                canvas_w = canvas_w / 2;
                canvas_h = canvas_h / 2;
            }
            canvas_target.width = canvas_w;
            canvas_target.height = canvas_h;
            lib.canvas_model4 = new Chart(canvas_target.getContext("2d")).Doughnut(doughnutData, {segmentShowStroke: false});
        }
    }
    return {
        init: lib.init
    }
})(org);
wlb.ready({
    app: function (mixins) {
        function connect(data) {
            org.ajax({
                url: '/accounts/token/login/ajax/',
                type: 'post',
                data: {
                    token: data.tk,
                    secret_key: data.secretToken,
                    ts: data.ts
                },
                success: function (data) {

                    org.finance.init()
                }
            })
        }

        mixins.shareData({title: '2015年，我终于拥有了自己的荣誉标签:...', content: '我就是我，不一样的烟火。刚出炉的荣誉标签，求围观，求瞻仰。'})
        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
                $('.client-login-alert').show().on('click', function () {
                    mixins.loginApp({refresh: 1, url: ''})
                })
                $('.login--alert-opeartion').on('click', function () {
                    $('.client-login-alert').hide()
                })

            } else {
                connect(data)
            }
        })


    },
    other: function () {
        org.finance.init()
    }
})

