org.area = (function (org) {
    var lib = {
        init: function () {
            lib.slide();

            var page = 2, pagesize = 2, latestPost = false;
            $('.area-latest-btn').on('click', function () {
                if (latestPost) return;

                org.ajax({
                    url: '/api/m/area/fetch/',
                    data: {
                        page: page,
                        pagesize: pagesize
                    },
                    beforeSend: function(){
                        latestPost = true
                        $('.area-latest-btn').text('加载中别急...')
                    },
                    success: function (data) {
                        page++;
                        $('.area-latest-push').append(data.html_data);
                        if (data.page >= data.all_page) {
                            $('.area-latest-more').html('没有更多了');
                        }
                    },
                    error: function (xhr) {
                        alert(xhr)
                    },
                    complete: function(){
                        latestPost = false;
                        $('.area-latest-btn').text('查看更多');
                    }

                })
            })
        },
        slide: function () {
            var myswiper = new Swiper('.swiper-container', {
                loop: false,
                lazyLoading: false,
                onSliderMove: function (swiper) {
                    var translateX = -(swiper.getWrapperTranslate() / 2)
                    $('.slide-bottom').css('-webkit-transform', 'translate3d(' + translateX + 'px, 0, 0)')
                },
                onTouchEnd: function (swiper) {
                    var translateX = 100 * swiper.activeIndex + '%';
                    $('.slide-bottom').css('-webkit-transform', 'translate3d(' + translateX + ', 0, 0)')
                },
                onSlideChangeStart: function (swiper) {
                    var translateX = 100 * swiper.activeIndex + '%';
                    $('.slide-bottom').css('-webkit-transform', 'translate3d(' + translateX + ', 0, 0)')

                    if(swiper.activeIndex === 1 && $('.area-milepost').attr('data-active') != 'true'){
                        doing(1, function(){
                            $('.area-milepost-loading').hide()
                        })
                    }
                }
            });
            $('.tab-nav li').on('touchend click', function () {
                var index = $(this).index();
                $(this).addClass('active').siblings().removeClass('active')
                myswiper.slideTo(index, 400, true);
            });

            var milepost = false
            $('.area-milepost-btn').on('click', function(){
                if (milepost) return;
                var page = parseInt($('.area-milepost').attr('data-page')) + 1;
                doing(page)
            });


            function doing(page, callback){
                org.ajax({
                    url: '/api/m/app_memorabilia/',
                    data: {
                        page: page,
                        pagesize: 2
                    },
                    beforeSend: function(){
                        milepost = true
                        $('.area-milepost-btn').text('加载中别急...')
                    },
                    success: function(result){
                        if(result.all_page > result.page){
                            $('.area-milepost-more').show()
                        }else{
                            $('.area-milepost-more').html('没有更多了，呵呵')
                        }
                        $('.area-milepost').attr({'data-active': true, 'data-page': result.page});
                        $('.area-milepost-push').append(result.html_data)
                        callback && callback(result)
                    },
                    complete: function(){
                        milepost = false;
                        $('.area-milepost-btn').text('查看更多');
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