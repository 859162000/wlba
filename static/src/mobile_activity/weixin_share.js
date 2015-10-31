(function(){
    window.alert = function(txt, callback){
        if(document.getElementById("alert-cont")){
            document.getElementById("alertTxt").innerHTML = txt;
            document.getElementById("popubMask").style.display = "block";
            document.getElementById("alert-cont").style.display = "block";
        }else{
            var shield = document.createElement("DIV");
            shield.id = "popubMask";
            shield.style.cssText="position:fixed;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
            var alertFram = document.createElement("DIV");
            alertFram.id="alert-cont";
            alertFram.style.cssText="position:fixed;top:23%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
            strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 0.8rem .75rem;margin-top:.3rem;height:15rem;overflow-y:auto'>"+txt+"</div>";
            strHtml +=" <div class=\"popub-footer\" style=\"width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;\" onclick=\"doOk()\">确认</div>";
            alertFram.innerHTML = strHtml;
            document.body.appendChild(alertFram);
            document.body.appendChild(shield);
            this.doOk = function(){
                alertFram.style.display = "none";
                shield.style.display = "none";
                callback && callback();
            };
        }
        document.body.onselectstart = function(){return false;};
    };

    function getQueryStringByName(name){
        var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
        if(result == null || result.length < 1){
         return '';
        }
        return result[1];
    }

    //微信分享
    var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
    org.ajax({
        type : 'GET',
        url : '/weixin/api/jsapi_config/',
        dataType : 'json',
        success : function(data) {
            //请求成功，通过config注入配置信息,
            wx.config({
                debug: false,
                appId: data.appId,
                timestamp: data.timestamp,
                nonceStr: data.nonceStr,
                signature: data.signature,
                jsApiList: jsApiList
            });
        }
    });

    var phoneNum = getQueryStringByName('phone') == '' ? '' : getQueryStringByName('phone');

    wx.ready(function(){

        var host = 'https://www.wanglibao.com',
            shareName = '有个红包一直拽在手里，今天我想要送给你',
            shareImg = host + '/static/imgs/mobile/share_logo.png',
            shareLink = host + '/activity/share/index/?parentPhone='+phoneNum,
            shareMainTit = '有个红包一直拽在手里，今天我想要送给你',
            shareBody = '领取网利宝580元现金红包,同时可为好友赢得最高80元红包奖励'
        //分享给微信好友
        org.onMenuShareAppMessage({
            title: shareMainTit,
            desc: shareBody,
            link: shareLink,
            imgUrl: shareImg
        });
        //分享给微信朋友圈
        org.onMenuShareTimeline({
            title: '[有人@我]给我们的友情添点真金白银，一人￥580',
            link : shareLink,
            imgUrl: shareImg
        })
        //分享给QQ
        org.onMenuShareQQ({
            title: shareMainTit,
            desc: shareBody,
            link : shareLink,
            imgUrl: shareImg
        })
    })

    $('#rule').on('click',function(){
        alert($('.rule-win').html())
    })

    $('#more').on('click',function(){
        $('.alertWin,.page').show();
    })
    $('.page').on('click',function(){
        $('.alertWin,.page').hide();
    })
})();

org.shareIndex = (function(org){
    var lib = {
        init:function(){
            lib.phoneFun();
            lib.receiveFun();
            lib.ruleSelect();
            var height = window.innerHeight;
            $('.share').css({'min-height': height});
        },
        phoneFun:function(){
            $('#iphone').on('focus',function(){
                var phone = $.trim($('#iphone').val());
                if(phone == '输入手机号') {
                    $('#iphone').val('');
                }
            })
            $('#iphone').on('blur',function(){
                var phone = $.trim($('#iphone').val());
                if(phone == '输入手机号' || phone == '') {
                    $('#iphone').val('输入手机号');
                }else{
                    $('.error').text('');
                }
            })
        },
        receiveFun:function(){
            var parentPhone = lib._getQueryStringByName('parentPhone') == '' ? '' : lib._getQueryStringByName('parentPhone');
            $('#receive').on('click',function(){
                if(!$('#ruleLabel span').hasClass('noChecked')){
                    var phone = $.trim($('#iphone').val());
                    if(phone == '' || phone == '输入手机号'){
                        $('.error').text('请输入手机号');
                    }else{
                        if(!/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/.test(phone)){
                             $('.error').text('手机号格式不正确');
                        }else{
                            $('.error').text('');
                            org.ajax({
                                url: '/api/user_exists/'+phone+'/',
                                type: 'GET',
                                data: {},
                                success:function(data){
                                    if(data.existing){
                                        window.location.href = '/activity/share/old/?phone='+phone;
                                    }else{
                                        window.location.href = '/activity/share/new/?parentPhone='+parentPhone+'&phone='+phone;
                                    }
                                },
                                error: function (xhr) {
                                }
                            });
                        }
                    }
                }else{
                    alert('<div class="alertFont">请查看活动规则</div>');
                }
            })
        },
        ruleSelect:function(){
            $('#ruleLabel').on('click',function(){
                var span = $(this).find('span');
                span.hasClass('noChecked') ? span.removeClass('noChecked') : span.addClass('noChecked');
            })
        },
        _getQueryStringByName:function(name){
            var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
            if(result == null || result.length < 1){
             return '';
            }
            return result[1];
        }
    }
    return {
        init :lib.init
    }
})(org);

org.newUser = (function(org){
    var lib = {
        init:function(){
            var phone = lib._getQueryStringByName('phone') == '' ? '' :  lib._getQueryStringByName('phone');
            var parentPhone = lib._getQueryStringByName('parentPhone') == '' ? '' :  lib._getQueryStringByName('parentPhone');
            $('#iphoneVal').text(phone);
            $('#goRegister').on('click',function(){
                window.location.href = 'weixin/regist/?parentPhone='+parentPhone+'&phone='+phone;
            })
            var height = window.innerHeight;
            if(height >= 1136){
                $('.wanglibao').css({'margin-top':'20%'});
            }
        },
        _getQueryStringByName:function(name){
            var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
            if(result == null || result.length < 1){
             return '';
            }
            return result[1];
        }
    }
    return {
        init :lib.init
    }
})(org);

org.shareFun = (function(org){
    var lib = {
        init:function(){
            var height = window.innerHeight;
            if(height >= 1136){
                $('.wanglibao').css({'margin-top':'20%'});
            }
        }
    }
    return {
        init :lib.init
    }
})(org);

;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if(src){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);


