
org.checin_in = (function (org) {
    var lib = {
        init: function(){

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
        alert('open in app!')
    }
})

