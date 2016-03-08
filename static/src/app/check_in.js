
org.checin_in = (function (org) {
    var lib = {
        init: function(){
            $('.icon-status').on('click', function(){
                lib.checkInOpeartion('sign_in', function(data){
                    if(data.data.status){
                        console.log('签到成功')
                    }

                })
            })
            lib.fetch();
        },
        listen: function(){

        },
        touchGift: function(){

        },
        share: function(result){
            $('.share-status').addClass('rm-loading');
            if(result.data.share.status){
                $('.share-status').find('.op-dec-title ').text('今日已分享')
            }else{
                $('.share-status').find('.op-dec-title ').text('今日未分享')
            }
            $('.share-status').find('.op-dec-detail').text('分享得双倍')
        },
        signIn: function(status, amount){
            $('.checIn-status').addClass('rm-loading');
            if(status){
                $('.checIn-status').find('.op-dec-title').text('今日已签到')
            }else{
                $('.checIn-status').find('.op-dec-title').text('今日未签到')
            }
            $('.checIn-status').find('.op-dec-detail').text('+'+amount+'体验金');
        },
        steriousGift:function(acount){
            $('.bar-content').text('距离神秘礼包还有'+acount+'天')
        },
        process: function(result){
            var str = "<div class='check-in-process-line'></div>";
                str +="<div class='check-in-flag-lists'>";
            var $process = $('.check-in-process');
            var itemStart =  result.data.sign_in.start_day;
            var itemEnd =itemStart + result.data.sign_in.nextDayNote -1;
            $process.addClass('rm-loading');
            var itemStatus = '';
            var continueDay = result.data.sign_in.continue_days;
            var currentDay = result.data.sign_in.current_day;
            var giftStatus = result.data.sign_in.continueGiftFetched;
            for(var i= itemStart; i <= itemEnd;i++){
                itemStatus = '';

                if(i <= continueDay){
                    //已签到的天数
                    itemStatus += " active-did "
                }

                if(i == currentDay){
                    //当天是否签到
                    itemStatus += " active-doing"
                }

                if(i == itemEnd){
                    //礼物所在天数
                    itemStatus = giftStatus ? "active-gift-open " : "active-gift ";
                }

                str += "<div data-continue='"+i+"' class='flag-items "+itemStatus+"'>";
                str += "<div class='circle-item-warp'>";
                str += "<div class='circle-item'>";
                str += "<div class='circle-min'></div>"
                str += "<div class='circle-animate'></div>"
                str += "<div class='check-in-flag'></div>"
                str += "</div>";
                str += "</div>";
                str += "<div class='text-item'>"+i+"天</div>"
                str += "</div>";
            }
            str += '</div>';
            return $process.append(str)
        },
        checkIn: function(result){
            var _self = this;

            var continue_days = result.data.sign_in.continue_days;

            if(!result.data.sign_in.status){
                _self.checkInOpeartion('sign_in', function(data){
                    if(data.data.status){
                        console.log('今天签到成功')
                        _self.checkInAlert('flag', '今日签到成功！获得'+data.data.experience_amount+'元体验金', '在(我的账户－体验金)中查看', function(){
                            triggerUI(data.data.continue_days)
                            _self.signIn(true, data.data.experience_amount)
                        })
                    }
                    continue_days = data.data.continue_days;
                    function triggerUI(count){
                        $.each($('.flag-items'), function(){
                            if($(this).attr('data-continue') * 1 == count){
                                $(this).addClass('active-did active-doing')
                            }
                        })
                    }
                })
            }

            $('.active-gift').on('click', function(){
                if(result.data.sign_in.nextDayNote == 1){
                    if(result.data.sign_in.continueGiftFetched){
                        console.log('礼物已另取锅了')
                    }else{
                        _self.fetchGift(continue_days)
                    }
                }else{
                    alert('还未到达礼品日！')
                }
            })
        },
        checkInOpeartion: function(action_type, callback){
            var _self = this;
            org.ajax({
                url: '/weixin/daily_action/',
                type: 'post',
                data: {
                    action_type: action_type
                },
                success: function(data){
                    callback && callback(data)
                }
            })
        },
        fetchGift: function(days){
            var _self = this;
            org.ajax({
                url: '/weixin/continue_action_reward/',
                type: 'post',
                data: {
                    days: days
                },
                success: function(data){
                    if(data.ret_code ===0){
                        _self.checkInAlert('flag', data.message, '在(我的账户)中查看')
                        $('.active-gift-open').addClass('.active-gift-open')
                    }

                    if(data.ret_code < 0){
                        alert(data.message)
                    }
                }
            })
        },
        fetch: function(){
            var _self = this;
            org.ajax({
                url: '/weixin/sign_info/',
                type: 'GET',
                success: function(data){
                    _self.signIn(data.data.sign_in.status, data.data.sign_in.amount)
                    _self.share(data)
                    _self.steriousGift(data.data.sign_in.mysterious_day)
                    _self.process(data)
                    _self.checkIn(data)
                }
            })
        },
        checkInAlert: function(type, giftText,whereText, callback){
            var $target = $('.check-in-alert-layout');
            var types = {
                'gift': 'overflow-gift',
                'flag': 'overflow-flag',
                'share': 'overflow-share'
            }
            $target.find('#check-body-overflow-icon').removeAttr('class').addClass(types[type])
            $target.find('.check-body-gift-information').text(giftText)
            $target.find('.check-body-where-information').text(whereText)
            $target.show()
            $('.check-body-opeartion-btn').on('click',function(){
                $target.hide()
                callback && callback()
            })
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
                    org.checin_in.init()
                }
            })
        }
        //mixins.shareData({title: '2015年，我终于拥有了自己的荣誉标签:...', content: '我就是我，不一样的烟火。刚出炉的荣誉标签，求围观，求瞻仰。'})
        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
                finance_alert.show('你还没有登录哦，登录获取更多资讯吧', function(mixin){
                    mixin.loginApp({refresh: 1, url: ''})
                },mixins)

            } else {
                connect(data)
            }
        })


    },
    other: function () {
        org.checin_in.init()
        //alert('open in app!')
    }
})

