wlb.ready({
    app: function (mixins) {
        $('#recharge').on('click',function(){
            mixins.rechargeApp({refresh: 1, url: 'https://staging.wanglibao.com/activity/experience/app_detail'})
        })
    },
    other: function () {
        $('#recharge').on('click',function(){
            window.location.href = '/weixin/recharge/';
        })
    }
})