$('.two-xiangqing').click(function () {
    window.location.href = '/activity/app_noviceDecember_h5/';
})
$('.two-bu').click(function () {
    $('#two-mov-ice').show();
    $('.mov').html('您可以通过电脑端登录网利宝账户，在“我的账户”－“自动投标”内进行自动投标功能设置。');
});
$('.ice-button').click(function () {
    $('#two-mov-ice').hide();
})
var login = false;
wlb.ready({
    app: function (mixins) {
        $('.two-buttonmon,.two-buttontt').click(function () {
            mixins.jumpToManageMoney();
        })

        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
                login = false;
                $('.two-buttonn,.two-buttonrenzheng').click(function () {
                     mixins.registerApp();
                });


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
                        $('.two-buttonn,.chart1-button0').click(function () {
                            $('#two-mov-ice').show();
                            $('.mov').html('您已是网利宝用户，无需再注册');
                        });
                        $('.two-buttonrenzheng').click(function () {
                            verify();
                        });

                    }

                })
                function verify() {
                    org.ajax({
                        url: '/api/has_validate/',
                        type: 'POST',
                        success: function (data) {
                            console.log(data)
                            if (data.ret_code == 0) {
                                $('#two-mov-ice').show();
                                $('.mov').html('您已是实名认证用户，无需再认证');
                            } else if (data.ret_code == 1) {
                                $('#two-mov-ice').show();
                                $('.mov').html('请到“我的账户”－“设置”内进行实名认证');
                            }
                        }

                    })

                }


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
                if (data1.login == true) {
                    $('.two-buttonn,.chart1-button0').click(function () {
                        $('#two-mov-ice').show();
                        $('.mov').html('您已是网利宝用户，无需再注册');
                    });
                    $('.two-buttonrenzheng').click(function () {
                        verify();
                    });
                } else {
                    $('.two-buttonn,.two-buttonrenzheng').click(function () {
                        window.location.href = '/weixin/regist/';
                    });


                }
                ;

            }
        });
        function verify() {
            org.ajax({
                url: '/api/has_validate/',
                type: 'POST',
                success: function (data) {
                    console.log(data)
                    if (data.ret_code == 0) {
                        $('#two-mov-ice').show();
                        $('.mov').html('您已是实名认证用户，无需再认证');
                    } else if (data.ret_code == 1) {
                        $('#two-mov-ice').show();
                        $('.mov').html('请到“我的账户”内进行实名认证');
                    }
                }

            })

        }

        $('.two-buttonmon,.two-buttontt').click(function () {
            window.location.href = '/weixin/list/';
        })

    }
})