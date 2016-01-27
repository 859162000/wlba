require.config({
    paths: {
        'jquery.animateNumber': 'lib/jquery.animateNumber.min',
        'countdown': 'model/countdown'
    },
    shim: {
        'jquery.animateNumber': ['jquery'],
        'jquery.modal': ['jquery']
    }
});

require(['jquery', 'jquery.animateNumber', 'countdown'], function ($) {

    //number adminante
    var $num = $('.num-space')
    $num.each(function () {
        var amount = parseInt($(this).attr('data-number')).toString(),
            type = $(this).attr('data-type');
        $(this).append(amountGe(amount, type));
    })
    function amountGe(value, type) {
        var len = value.length, str = '';
        reType = type == 'man' ? '人' : '元';
        if (len > 8) {
            str = isNode(value.substr(0, len - 8), '亿') + isNode(value.substr(-8, 4), '万');
        } else {
            str = isNode(value.substr(0, len - 4), '万');
        }
        function isNode(substr, text) {
            if (parseInt(substr) > 0) {
                return " <span class='num-animate'>" + parseInt(substr) + "</span> <span class='num-text'>" + text + '</span>';
            }
            return '';
        }

        return str
    }

    $('.num-animate').each(function () {
        var key = parseInt($(this).html());
        $(this).prop('number', 0).animateNumber({
            number: key,
        }, 1000);
    })


    //倒计时
    var
        time = $('.recommend_time').attr('data-update'),
        endTime = new Date(time.replace(/-/g, "/"));
    $('.recommend_time').countdown(endTime);

    //nav fixed
    var $nav = $('.g-nav-warp');
    $(window).scroll(function () {
        $(window).scrollTop() > 80 ? $nav.addClass('g-nav-fixed').animate({'top': 0}, 300) : $nav.stop(!0, !0).removeClass('g-nav-fixed').removeAttr('style');
    })

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
    //余额显示
    var $balanceHide = $('.icon-eye03'),
        $balanceShow = $('.icon-eye02'),
        $balanceShowCont = $(".landed-cont-show"),
        $balanceHideCont = $(".landed-cont-hide");
    $balanceHide.on('click', function () {
        $balanceHide.hide()
        $balanceShow.show()
        $balanceHideCont.hide()
        $balanceShowCont.show()
    });
    $balanceShow.on('click', function () {
        $balanceShow.hide()
        $balanceHide.show()
        $balanceHideCont.show()
        $balanceShowCont.hide()
    })

    //扫描送红包
    var scrollTimer = null;
    $(window).on('scroll', function () {
        if (scrollTimer) {
            clearTimeout(scrollTimer)
        }
        scrollTimer = setTimeout(function () {
            var $scroll = $(document).scrollTop();
            if ($scroll > ($(document).height() * 0.4)) {
                $('.bonus-icon').animate({'top': '30%'}, 200);
            } else {
                $('.bonus-icon').animate({'top': '60%'}, 200);
            }
        }, 200);
    });


    $('.bonus-icon').on('click', function () {
        $('.bonus-img,.page').show();
    });
    $('.close').on('click', function () {
        $('.bonus-img,.page').hide();
    });

    function wxShareIcon() {
        var docleft = document.body.clientWidth;
        var left = (docleft - $('.bonus-icon').width());
        $('.bonus-icon').css({'left': left});
    }

    //wxShareIcon()
    window.onresize = function () {
        wxShareIcon();
    };

    //new year animate

    var animate_count = 0,
        animate_setTimeout = null,
        $leoLayout = $('.leo-layout'),
        $coupletCount = $('.couplet-count'),
        $counplet = $('.couplet');
    isImgLoad(function () {
        function animate() {
            if (animate_count % 2 === 0) {
                $leoLayout.addClass('new-year-animate-active')
            } else {
                $leoLayout.addClass('new-year-animate-even')
            }

            $coupletCount.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
                if (animate_count % 2 === 0) {
                    $leoLayout.removeClass('new-year-animate-active')
                    $counplet.css('transform', 'translate3d(0, 0, 0)')
                } else {
                    $leoLayout.removeClass('new-year-animate-even')
                    $counplet.css('transform', 'translate3d(0, -420px, 0)')
                }
                animate_count++
                if (animate_count >= 17) {
                    window.clearTimeout(animate_setTimeout)
                }
            })

            animate_setTimeout = window.setTimeout(animate, 5000)
        }

        animate()
    });

    //首页动画，如果动画所涉及的图片没有加载完成，不会触发动画
    var t_img;
    var isLoad = true;

    function isImgLoad(callback) {
        $('.leo-imgs').each(function () {
            if (this.height === 0) {
                isLoad = false;
                return false;
            }
        });
        if (isLoad) {
            clearTimeout(t_img);
            callback();
        } else {
            isLoad = true;
            t_img = setTimeout(function () {
                isImgLoad(callback);
            }, 500);
        }
    }

    ~function show_newyear() {
        if ($(window).height() > 700) {
            $('.g-new-year-bottom-warp').show()
        }
    }()
});