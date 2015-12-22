

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
            var host = 'https://www.wanglibao.com',
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

org.ui = (function(){
    var lib = {
        _alert: function(txt, callback){
            if(document.getElementById("alert-cont")){
                document.getElementById("alertTxt").innerHTML = txt;
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
            }else{
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText="position:absolute;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
                var alertFram = document.createElement("DIV");
                alertFram.id="alert-cont";
                alertFram.style.cssText="position:absolute; top:35%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
                strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 1.25rem .75rem;'>"+txt+"</div>";
                strHtml += " <div class='popub-footer' style='width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;'>确认</div>";
                alertFram.innerHTML = strHtml;
                document.body.appendChild(alertFram);
                document.body.appendChild(shield);

                $('.popub-footer').on('click',function(){
                    alertFram.style.display = "none";
                    shield.style.display = "none";
                    callback && callback();
                })
            }
            document.body.onselectstart = function(){return false;};
        }
    }

    return {
        alert : lib._alert,
    }
})();
org.weChatStart = (function(org){
    var lib = {
        $captcha_img : $('#captcha'),
        $captcha_key : $('input[name=captcha_0]'),
        init:function(){
            lib._fetchPack()
            lib._captcha_refresh()
        },
        _fetchPack: function(){
            var
                $submit  = $('.webpack-btn-red'),
                phoneVal = $('input[name=phone]'),
                code = $('input[name=code]'),
                postDo = false;

            $submit.on('click', function(){
                if(postDo) return

                $submit.html('领取中...');
                var ops = {
                    phone : phoneVal.val() * 1,
                    activity : $(this).attr('data-activity'),
                    orderid : $(this).attr('data-orderid'),
                    openid : $(this).attr('data-openid'),
                    code : code.val()
                }

                if(!lib._checkPhone(ops.phone)) return ;
                //var ele = $('.code');
                //var curHeight = ele.height();
                //var autoHeight = ele.css('height', 'auto').height();
                //ele.height(curHeight).animate({height: autoHeight},500);

                if(ops.code =='') {
                    $('.code-sign').show();
                    return;
                }else{
                    $('.code-sign').hide();
                }
                org.ajax({
                    url: '/api/weixin/share/has_gift/',
                    type: 'POST',

                    data: {
                        'openid': ops.openid,
                        'phone_num': ops.phone,
                        'order_id': ops.orderid,
                        'code': ops.code
                    },
                    dataType : 'json',
                    success: function(data){
                        if(data.has_gift == 'true'){
                            org.ui.alert(data.message, function(){
                                window.location.href = '/weixin_activity/share/'+ops.phone+'/'+ops.openid+'/'+ops.orderid+'/'+ops.activity+'/';
                            });
                        }else if(data.has_gift == 'false'){
                            window.location.href = '/weixin_activity/share/'+ops.phone+'/'+ops.openid+'/'+ops.orderid+'/'+ops.activity+'/';
                        }
                    },
                    error: function(data){
                        org.ui.alert(data)
                    },
                    complete: function(){
                        postDo = false;
                        $submit.html('立即领取');
                    }
                })

            });

        },
        _checkPhone : function(val){
            var isRight = false,
                $sign = $('.phone-sign'),
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
            re.test($.trim(val)) ? ($sign.hide(), isRight = true) : ($sign.show(),isRight = false);
            return isRight;
        },
        _captcha_refresh :function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function(res) {
                lib.$captcha_img.attr('src', res['image_url']);
                lib.$captcha_key.val(res['key']);
            });
        }
    }
    return {
        init : lib.init
    }
})(org);

org.weChatDetail = (function(org){
    var lib = {
        init:function(){
            /*window.onload = function(){
              if($('#amount').attr('data-hasgift') == 'true'){
                 org.ui.alert('您已经领取过礼物了！');
              }
            }*/
        },
    }
    return {
        init : lib.init
    }
})(org);

org.weChatEnd = (function(org){
    var lib = {
        init:function(){

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