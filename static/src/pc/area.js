require.config({
  paths: {
    'csrf' : 'model/csrf'
  }
});

require(['jquery', 'csrf'], function ($) {

    var dopost= false;
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

    var pagesize = 6;
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

    function postDate(data, target, cover, callback){
        $.ajax({
            url: '/activity/list/',
            type: "GET",
            data: data,
            beforeSend: function(){
                dopost = true
            },
            complete: function(){
                dopost = false
            }
        }).done(function (result) {
            if(result.page >= result.all_page){
                $('.area-list-more').hide();
                $('.area-list-unmore').show();
            }else{
                $('.area-list-more').show();
                $('.area-list-unmore').hide()
            }

            cover ? $('.area-active-item').html(result.html_data): $('.area-active-item').append(result.html_data);
            target.attr('data-page', result.page).siblings().attr('data-page', 0);
            callback && callback(result)
        }).fail(function (xhr) {

        });
    }

});