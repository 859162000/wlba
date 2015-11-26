org.area = (function (org) {
    var lib = {
        init: function () {
            var page = 2, pagesize = 2;
            $('.area-latest-btn').on('click', function(){
                org.ajax({
                    url: '/api/m/area/upload/',
                    data: {
                        page: page,
                        pagesize: pagesize
                    },
                    success:function(data){
                        page++;
                        $('.area-latest-push').append(data.html_data);
                        if(data.page >= data.all_page){
                            $('.area-latest-more').html('没有更多了');
                        }
                    },
                    error: function(xhr){
                        alert(xhr)
                    }

                })
            })
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