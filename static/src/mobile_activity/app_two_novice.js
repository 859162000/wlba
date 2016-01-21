var login = false;
wlb.ready({
    app: function (mixins) {
        $('.two-buttonmon,').click(function () {
            mixins.jumpToManageMoney();
        })

        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
                login = false;


            } else {
                login = true;
                org.ajax({
                    url: '/accounts/token/login/ajax/',
                    type: 'post',
                    data: {
                        token: data.tk,
                        secret_key: data.secretToken,
                        ts: data.ts
                    },
                    success: function (data1) {

                    }

                })


            }


        })

    },
    other: function () {
        var boy = $(document.body).height();
        $('#two-mov-ice').css({'height': boy});
        org.ajax({
            url: '/api/user_login/',
            type: 'post',
            success: function (data1) {
                if(data1.login==true){
                    //alert(123)
                };
            }
        });

    }
})