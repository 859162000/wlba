org.area = (function (org) {
    var lib = {
        init: function () {
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


    }
    return {
        init: lib.init
    }
})(org);

org.milepost = (function (org) {
    var lib = {
        init: function () {
            lib.slide();

        },

        slide: function () {
            var milepost = false,
                $milepostBtn = $('.area-milepost-btn'),
                $milepostMore = $('.area-milepost-more'),
                $milepostPush =$('.area-milepost-push'),
                $slideLine = $('.slide-bottom'),
                $milepost = $('.area-milepost');


            var page = 1;
            $milepostBtn.on('click', function(){
                if (milepost) return;
                page = page + 1;
                doing(page);
            });


            function doing(page, callback){
                org.ajax({
                    url: '/api/m/app_memorabilia/',
                    data: {
                        page: page,
                        pagesize: 6
                    },
                    beforeSend: function(){
                        milepost = true;
                        $milepostBtn.text('加载中...')
                    },
                    success: function(result){
                        var html_data = result.html_data;
                        if(result.all_page > result.page){
                            $milepostMore.show()
                        }else{
                            $milepostMore.html('没有更多了!')
                        }
                        $milepost.attr({'data-active': true, 'data-page': result.page});

                        if(result.list_count === 0){
                            html_data = "<div class='unactivty'>暂无大事件！</div>";
                        }
                        $milepostPush.append(html_data);
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