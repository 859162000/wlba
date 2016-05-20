wlb.ready({
    app: function (mixins) {
        mixins.rechargeApp({refresh: 1, url: 'https://staging.wanglibao.com/activity/experience/app_detail'})
    },
    other: function () {
        //org.feast.init()
    }
})