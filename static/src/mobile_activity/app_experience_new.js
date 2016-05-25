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
                }
            })
        }
        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
            } else {
                connect(data)
                $('#recharge').on('click',function(){
                    mixins.rechargeApp({refresh: 1, url: 'https://staging.wanglibao.com/activity/experience/app_detail'})
                })
            }
        })
    },
    other: function () {
        $('#recharge').on('click',function(){
            window.location.href = '/weixin/recharge/';
        })
    }
})