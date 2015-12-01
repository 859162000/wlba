require.config({
  paths: {
    'csrf' : 'model/csrf'
  }
});

require(['jquery', 'csrf'], function ($) {

    var dopost= false, pagesize = 6;

    $('#area-nav li').on('click', function () {
        if (dopost) return
        var index = $(this).index();
        $(this).addClass('active').siblings().removeClass('active')
        $('.active_slide').animate({
            left: 155 * index
        }, 300)

        postDate({
            'category': $(this).attr('data-category'),
            'page': parseInt($(this).attr('data-page')) + 1,
            'pagesize': pagesize
        }, $(this), true)
    });

    $('.area-list-more').on('click', function(){
        if (dopost) return
        $.each($('#area-nav li'), function(i,dom){
            if($(this).hasClass('active')){
                postDate({
                    'category': $(this).attr('data-category'),
                    'page': parseInt($(this).attr('data-page')) + 1,
                    'pagesize': pagesize
                }, $(dom), false)
            }
        })

    });


    var $areaLoding = $('.area-mask-warp'),
        $more = $('.area-list-more'),
        $unMore = $('.area-list-unmore'),
        $item = $('.area-active-item');
    function postDate(data, target, cover, callback){
        $.ajax({
            url: '/activity/area/filter/',
            type: "GET",
            data: data,
            beforeSend: function(){
                dopost = true
                $areaLoding.show();
            },
            complete: function(){
                dopost = false
                $areaLoding.hide();
            }
        }).done(function (result) {
            var html_data = result.html_data;

            if(result.page >= result.all_page){
                $more.hide();
                cover ? $unMore.hide(): $unMore.show();;
            }else{
                $more.show();
                $unMore.hide();
            }

            if(cover && result.list_count === 0){
                html_data = '该分类下没有活动！';
            }

            cover ? $item.html(html_data): $item.append(html_data);

            target.attr('data-page', result.page).siblings().attr('data-page', 0);
            callback && callback(result)
        }).fail(function (xhr) {
            alert(xhr)
        });
    }

});