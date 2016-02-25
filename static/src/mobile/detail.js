import { ajax } from './mixins/api'

(()=>{
    /**
     * 公司信息tab
     */
    $('.toggleTab').on('click', function () {
        $(this).siblings().toggle();
        $(this).find('span').toggleClass('icon-rotate');
    })

    /**
     * 倒计时
     */
    const countDown =  $('#countDown');

    const countDown_func  = (target) => {
        const endTimeList = target.attr('data-left').replace(/-/g, '/');
        const TimeTo = function (dd) {
            let t = new Date(dd),
                n = parseInt(new Date().getTime()),
                c = t - n;
            if (c <= 0) {
                target.text('活动已结束')
                clearInterval(window['interval']);
                return
            }
            let ds = 60 * 60 * 24 * 1000,
                d = parseInt(c / ds),
                h = parseInt((c - d * ds) / (3600 * 1000)),
                m = parseInt((c - d * ds - h * 3600 * 1000) / (60 * 1000)),
                s = parseInt((c - d * ds - h * 3600 * 1000 - m * 60 * 1000) / 1000);
            m < 10 ? m = '0' + m : '';
            s < 10 ? s = '0' + s : '';
            target.text(d + '天' + h + '小时' + m + '分' + s + '秒');
        }
        window['interval'] = setInterval(function () {
            TimeTo(endTimeList);
        }, 1000);
    }
    countDown.length > 0 && countDown_func(countDown);

    /**
     * 动画
     */

    $(function () {
        const $progress = $('.progress-percent');
        setTimeout(function () {
            var percent = parseFloat($progress.attr('data-percent'));
            if (percent == 100) {
                $progress.css('margin-top', '-10%');
            } else {
                $progress.css('margin-top', (100 - percent) + '%');
            }
            setTimeout(function () {
                $progress.addClass('progress-bolang')
            }, 1000)
        }, 300)
    })
    /**
     * 微信分享自定义
     */
    const weixin_share = () => {
            var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ',];
            ajax({
                type: 'GET',
                url: lib.weiURL,
                dataType: 'json',
                success: function (data) {
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
            wx.ready(function () {
                var $productName = $('.product-name'),
                    $earningRate = $('.profit-txt'),
                    $period = $('.time-txt');

                var host = 'https://www.wanglibao.com',
                    shareName = $productName.attr('data-name'),
                    shareImg = host + '/static/imgs/mobile/share_logo.png',
                    shareLink = host + '/weixin/detail/' + $productName.attr('data-productID'),
                    shareMainTit = '我在网利宝发现一个不错的投资标的，快来看看吧',
                    shareBody = shareName + ',年收益' + $earningRate.attr('data-earn') + '%,期限' + $period.attr('data-period');
                //分享给微信好友
                wx.onMenuShareAppMessage({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg
                });
                //分享给微信朋友圈
                wx.onMenuShareTimeline({
                    title: shareMainTit,
                    link: shareLink,
                    imgUrl: shareImg
                })
                //分享给QQ
                wx.onMenuShareQQ({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg
                })
            })
        }
    weixin_share()
})()