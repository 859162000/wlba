(function () {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            'activityRegister': 'activityRegister'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });

    require(['jquery', 'activityRegister'], function ($, re) {
        //注册
        re.activityRegister.activityRegisterInit({
            registerTitle: '领取580新用户红包',    //注册框标语
            isNOShow: '1',
            buttonFont: '立即注册'
        });

        //banner
        var currentBanner = 0, timer = null, speedBanner = 3000,
            banners = $('.slide-banner'),
            bannerCount = banners.length,
            anchors = $('.slide-anchor');
        switchBanner = function () {
            $(banners[currentBanner]).fadeOut();
            $(anchors[currentBanner]).toggleClass('active');
            currentBanner = (currentBanner + 1) % bannerCount;
            $(banners[currentBanner]).fadeIn();
            $(anchors[currentBanner]).toggleClass('active');
        };
        timer = setInterval(switchBanner, speedBanner);
        anchors.mouseover(function (e) {
            return clearInterval(timer);
        }).mouseout(function (e) {
            return timer = setInterval(switchBanner, speedBanner);
        });
        anchors.click(function (e) {
            e.preventDefault();
            var index = $(this).index();
            if (index !== currentBanner) {
                $(banners[currentBanner]).fadeOut();
                $(anchors[currentBanner]).toggleClass('active');
                $(banners[index]).fadeIn();
                $(anchors[index]).toggleClass('active');
                return currentBanner = index;
            }
        });


        var $num = $('.gv_tzh')
        $num.each(function () {
            var amount = parseInt($(this).attr('data-number')).toString(),
                type = $(this).attr('data-type');
            $(this).append(amountGe(amount, type));
        })
        function amountGe(value, type) {
            var len = value.length, str = '';
            // reType = type == 'man' ? '人' : '元';
            if (type == "amount") {
                if (len > 8) {
                    str = isNode(value.substr(0, len - 8), '亿') + isNode(value.substr(len - 8, 4), '万') + isNode(value.substr(len - 4, len), '元');
                } else {
                    str = isNode(value.substr(0, len - 4), '万') + isNode(value.substr(len - 4, len), '元');
                }
            } else {
                str = isNode(value.substr(0, len), '位小伙伴');
            }

            function isNode(substr, text) {
                if (parseInt(substr) > 0) {
                    return " <span class='num-animate'>" + parseInt(substr) + "</span> <span class='num-text'>" + text + '</span>';
                }
                return '';
            }

            return str
        }

        var login = $("#xun_login");
        login.on("click", function () {
            $(this).attr("href", "/accounts/login/?next=/activity/baidu_finance/")
        })


        var detail = $('.explain-detail');
        $('.rules-detail').on('click', function () {
            if (detail.hasClass('this-show')) {
                detail.animate({'height': 0}).removeClass('this-show')
            } else {
                detail.animate({'height': 155}).addClass('this-show')
            }

        })

    });
}).call(this);
