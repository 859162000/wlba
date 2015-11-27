org.area = (function (org) {
    var lib = {
        init: function () {
            lib.slide();

            var page = 2, pagesize = 6, latestPost = false;

            var $latest =$('.area-latest-btn'),
                $latestPush = $('.area-latest-push'),
                $latestMore = $('.area-latest-more');

            $latest.on('click', function () {
                if (latestPost) return;

                org.ajax({
                    url: '/api/m/area/fetch/',
                    data: {
                        page: page,
                        pagesize: pagesize
                    },
                    beforeSend: function(){
                        latestPost = true;
                        $latest.text('加载中...')
                    },
                    success: function (data) {
                        page++;
                        $latestPush.append(data.html_data);
                        if (data.page >= data.all_page) {
                            $latestMore.html('没有更多了!');
                        }
                    },
                    error: function (xhr) {
                        alert(xhr)
                    },
                    complete: function(){
                        latestPost = false;
                        $latest.text('查看更多');
                    }

                })
            })
        },

        slide: function () {

            var $slideLine = $('.slide-bottom'),
                $milepostLoad = $('.area-milepost-loading'),
                $milepost = $('.area-milepost'),
                myswiper = new Swiper('.swiper-container', {
                    loop: false,
                    lazyLoading: false,
                    onSliderMove: function (swiper) {
                        var translateX = -(swiper.getWrapperTranslate() / 2)
                        $slideLine.css('-webkit-transform', 'translate3d(' + translateX + 'px, 0, 0)')
                    },
                    onTouchEnd: function (swiper) {
                        var translateX = 100 * swiper.activeIndex + '%';
                        $slideLine.css('-webkit-transform', 'translate3d(' + translateX + ', 0, 0)')
                    },
                    onSlideChangeStart: function (swiper) {
                        var translateX = 100 * swiper.activeIndex + '%';
                        $slideLine.css('-webkit-transform', 'translate3d(' + translateX + ', 0, 0)')

                        if(swiper.activeIndex === 1 && $milepost.attr('data-active') != 'true'){
                            doing(1, function(){
                                $milepostLoad.hide()
                            })
                        }
                    }
                });

            $('.tab-nav li').on('touchend click', function () {
                var index = $(this).index();
                $(this).addClass('active').siblings().removeClass('active')
                myswiper.slideTo(index, 400, true);
            });

            var milepost = false,
                $milepostBtn = $('.area-milepost-btn'),
                $milepostMore = $('.area-milepost-more'),
                $milepostPush =$('.area-milepost-push');


            $milepostBtn.on('click', function(){
                if (milepost) return;
                var page = parseInt($milepost.attr('data-page')) + 1;
                doing(page)
            });


            function doing(page, callback){
                org.ajax({
                    url: '/api/m/app_memorabilia/',
                    data: {
                        page: page,
                        pagesize: 6
                    },
                    beforeSend: function(){
                        milepost = true
                        $milepostBtn.text('加载中...')
                    },
                    success: function(result){
                        if(result.all_page > result.page){
                            $milepostMore.show()
                        }else{
                            $milepostMore.html('没有更多了!')
                        }
                        $milepost.attr({'data-active': true, 'data-page': result.page});
                        $milepostPush.append(result.html_data);
                        callback && callback(result);
                    },
                    complete: function(){
                        milepost = false;
                        $milepostBtn.text('查看更多');
                    }
                })
            }
        },

    }
    return {
        init: lib.init
    }
})(org);

;
(function (org) {
    $.each($('script'), function () {
        var src = $(this).attr('src');
        if (src) {
            if ($(this).attr('data-init') && org[$(this).attr('data-init')]) {
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);