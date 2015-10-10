

var weChatShare = (function(org){
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
        wx.ready(function(){
            var host = 'https://staging.wanglibao.com',
                shareImg = host + '/static/imgs/mobile/weChat_logo.png',
                shareLink = $('input[name=url]').val(),
                shareMainTit = $('input[name=title]').val(),
                shareBody = $('input[name=content]').val();
            //分享给微信好友
            org.onMenuShareAppMessage({
                title: shareMainTit,
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg
            });
            //分享给微信朋友圈
            org.onMenuShareTimeline({
                title: shareMainTit,
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
})(org);

org.weChatStart = (function(org){
    var lib = {
        init:function(){
            lib._fetchPack()
        },
        _fetchPack: function(){
            var
                $submit  = $('.webpack-btn-red'),
                phoneVal = $('input[name=phone]');

            $submit.on('click', function(){
                var ops = {
                    phone : phoneVal.val() * 1,
                    activity : $(this).attr('data-activity'),
                    orderid : $(this).attr('data-orderid'),
                    openid : $(this).attr('data-openid'),
                }

                if(!lib._checkPhone(ops.phone)) return ;

                window.location.href = '/weixin_activity/share/'+ops.phone+'/'+ops.openid+'/'+ops.orderid+'/'+ops.activity+'/';
            });

        },
        _checkPhone : function(val){
            var isRight = false,
                $sign = $('.phone-sign'),
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
            re.test($.trim(val)) ? ($sign.hide(), isRight = true) : ($sign.show(),isRight = false);
            return isRight;
        }
    }
    return {
        init : lib.init
    }
})(org);

org.weChatDetail = (function(org){
    var lib = {
        init:function(){
            console.log('detail')
        },
    }
    return {
        init : lib.init
    }
})(org);

org.weChatEnd = (function(org){
    var lib = {
        init:function(){
            console.log('end')
        },
    }
    return {
        init : lib.init
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