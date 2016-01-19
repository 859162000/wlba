
var weChatShare = (function(org){
    var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
        org.ajax({
            type : 'GET',
            url : '/weixin/api/jsapi_config/',
            dataType : 'json',
            success : function(data) {
                //请求成功，通过config注入配置信息,
                wx.config({
                    debug: true,
                    appId: data.appId,
                    timestamp: data.timestamp,
                    nonceStr: data.nonceStr,
                    signature: data.signature,
                    jsApiList: jsApiList
                });
            }
        });
        wx.ready(function(){
            var host = 'https://www.wanglibao.com/',
                shareImg = host + '/static/imgs/mobile/weChat_logo.png',
                shareLink = window.location.href,
                shareMainTit = '2015年，含辛茹苦、呕心沥血的我，我终于拥有了自己的荣誉标签:...',
                shareBody = '我就是我，不一样的烟火。刚出炉的荣誉标签，求围观，求瞻仰。';
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

org.other_client = (function () {
    var lib = {
        init: function(){
            window.onload = function(){
                $('.client-loding-warp').hide()
            }
            lib.swiper()
            lib.switch_look()
        },
        swiper: function(){
              var swiper = new Swiper('.swiper-container', {
                    paginationClickable: true,
                    direction: 'vertical',
                    initialSlide: 0,
              });
        },
        switch_look: function () {
            var
                _self = this,
                tag_name = ['神经兮兮', '散财童子', '商界名流', '王者风范'],
                tag_detail = [
                    '总是看起来神叨叨的，对理财那点事非常敏感，总是不停地在规避自己眼中的“危险”。别人笑我太疯癫，我笑别人太天真。',
                    '充满活力的小孩心性，看见新鲜事物总忍不住尝试下，不安于安逸的花钱个性，成为一个人见人爱的散财童子。',
                    '脑子灵活，总是在默默地攒着金条，在精明商人的道路上越行越远。', '与生俱来的王者气质，热情又慷慨，花钱又大方，总有抢着买单的冲动'
                ],
                tag_look = ['look-1', 'look-2', 'look-3', 'look-4'];
            $('.touch-icon').on('click', function () {
                var index = _self._random();
                $(this).hide();
                $('.tv-title').html(tag_name[index])
                $('.tv-cont-dec').html(tag_detail[index])
                $('.tv-cont').addClass('ele-txt3')
                $('.share-page-look').animate({
                    opacity: 1
                },500, function(){
                    $(this).addClass(tag_look[index] + ' ele-ballon-two')
                })
            })
        },
        _random: function () {
            return Math.floor(Math.random() * 4);
        }
    }
    return {
        init: lib.init
    }
})()

 org.other_client.init()
