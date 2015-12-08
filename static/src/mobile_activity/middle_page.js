(function(org){
    var login = false;
    wlb.ready({
        app: function (mixins) {
            function canter(data){
               org.ajax({
                url: '/accounts/token/login/ajax/',
                type: 'post',
                data: {
                    token: data.tk,
                    secret_key: data.secretToken,
                    ts: data.ts
                },
                success: function (data) {
                    window.location.href= '/activity/experience/mobile/'

                },
                error: function(){
                   window.location.href= '/activity/experience/mobile/'
                }

            })
            }

            mixins.sendUserInfo(function (data) {
                if (data.ph == '') {
                    login = false;
                    canter(data)
                } else {
                    login = true;
                    canter(data)
                }
            })
        },
        other: function(){
        }
    })
})(org);
