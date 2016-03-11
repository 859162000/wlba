
org.ui = (function () {
    var lib = {
        _alert: function (txt, callback) {
            if (document.getElementById("alert-cont")) {
                document.getElementById("alertTxt").innerHTML = txt;
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
            } else {
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText = "position:fixed;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
                var alertFram = document.createElement("DIV");
                alertFram.id = "alert-cont";
                alertFram.style.cssText = "position:fixed; top:35%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
                strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 1.25rem .75rem;'>" + txt + "</div>";
                strHtml += " <div class='popub-footer' style='width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;'>确认</div>";
                alertFram.innerHTML = strHtml;
                document.body.appendChild(alertFram);
                document.body.appendChild(shield);
            }
            $('.popub-footer').on('click', function () {
                $('#alert-cont, #popubMask').hide()
                callback && callback();
            })
            document.body.onselectstart = function () {
                return false;
            };
        }
    }

    return {
        alert: lib._alert
    }
})();
org.checin_in = (function () {
    var lib = {
        appShare: null,
        init: function(mixins){
            lib.appShare = mixins
            lib.fetch();
        },
        share: function(result){
            var
                _self = this,
                $share =  $('.share-status'),
                shareText = '',
                shareStaus = result.data.share.status;
            $share.addClass('rm-loading');

            function shareInfo(status){
                shareText = status ? '今日已分享' : '今日未分享';
                $share.find('.op-dec-title ').text(shareText);
                $share.find('.op-dec-detail').text('分享得双倍')
            }
            shareInfo(shareStaus)

            $('.icon-share').on('click',function(){
                if(shareStaus) return org.ui.alert('今天你已经分享过了')
                _self.appShare.touchShare({
                    title: '每日签到title',
                    content: '每日签到content',
                    shareUrl: 'http://192.168.20.45:8000/api/m/check-in-share/'
                })
            });

            try{
                _self.appShare.shareStatus(function(result){
                    _self.checkInAlert('share', '今日签到成功！获得'+result.data.experience_amount+'元体验金', '在(我的账户－体验金)中查看');
                    shareStaus = true;
                    shareInfo(shareStaus)
                })
            }catch(e){
                alert('open in app')
            }

        },
        signIn: function(status, amount){
            var $checkIn = $('.checIn-status'), checkInText ='';

            $checkIn.addClass('rm-loading');
            checkInText = status ? '今日已签到' : '今日未签到';
            $checkIn.find('.op-dec-title').text(checkInText);
            $checkIn.find('.op-dec-detail').text('+'+amount+'体验金');
        },
        steriousGift:function(acount){
            $('.bar-content').text('距离神秘礼包还有'+acount+'天')
        },
        process: function(result){
            var resultCopy = result.data.sign_in,
                itemStart =  resultCopy.start_day,
                itemEnd   = resultCopy.nextDayNote,
                continueDay = resultCopy.continue_days,
                currentDay = resultCopy.current_day,
                giftStatus = resultCopy.continueGiftFetched,
                itemStatus = '',
                $process = $('.check-in-process'),
                str = "<div class='check-in-process-line'></div>";
                str +="<div class='check-in-flag-lists'>";

            $process.addClass('rm-loading');
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
            var _self = this, resultCopy = result.data.sign_in;

            var continue_days = resultCopy.continue_days;

            if(!resultCopy.status){

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
                                $(this).addClass('active-did active-doing').siblings('.flag-items').removeClass('active-doing')
                            }
                        })
                    }

                })
            }

            $('.active-gift').on('click', function(){
                var giftDay = resultCopy.nextDayNote - resultCopy.continue_days;
                if(giftDay == 0){
                    if(resultCopy.continueGiftFetched){
                        console.log('礼物已另取锅了')
                    }else{
                        _self.fetchGift(continue_days)
                    }
                }else if(giftDay > 0){
                    console.log(giftDay)
                    org.ui.alert('还未到达礼品日！')
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
                        _self.checkInAlert('gift', data.message, '在(我的账户)中查看');
                        _self.steriousGift(data.mysterious_day)
                        $('.active-gift').addClass('active-gift-open')
                    }
                    if(data.ret_code < 0){
                        org.ui.alert(data.message)
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
})();


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
                    org.checin_in.init(mixins)
                }
            })
        }

        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
                mixins.loginApp({refresh: 1, url: ''})

            } else {
                connect(data)
            }
        })


    },
    other: function () {
        //org.checin_in.init()
        alert('guy ! open in app!')
    }
})

