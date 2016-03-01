require.config({
    paths: {
        'jquery.waypoints': 'lib/jquery.waypoints.min',
    },
    shim: {
        'jquery.waypoints': ['jquery'],
    }
});

require(['jquery', 'jquery.waypoints'], function ($, waypoints) {
    var waypoints = $('.model-animate').waypoint(function(direction) {
        var ele = $(this.element);
        var ele_id = parseInt($(this.element).attr('id').substring(19,20));
        ele.addClass('active').siblings('.model-animate').removeClass('active');
    }, {
      offset: -100
    })

    var
        $download_layout = $('.generalize-dec-pub'),
        $download_layout_copy = $('.generalize-dec-other'),
        $download_layout_RIGHT =$(window).width()- $download_layout.offset().left- $download_layout.width(),
        $download_layout_TOP = 965;

    var scrollTimer = null;
    $(window).on('scroll', function () {
        if (scrollTimer) {
            clearTimeout(scrollTimer)
        }
        scrollTimer = setTimeout(function () {
            repeat_sign($(window).scrollTop())
            if($(window).scrollTop() > $download_layout_TOP){
                if($(window).scrollTop() > 3768){
                    $download_layout.hide();
                    return $download_layout_copy.show()
                }else{
                    $download_layout.show();
                    $download_layout_copy.hide()
                }
                $download_layout.addClass('generalize-dec-fixed').css('right', $download_layout_RIGHT).animate({top: 150}, 300)
            }else if($(window).scrollTop() < $download_layout_TOP){
                $download_layout.stop(!0, !0).removeAttr('style').removeClass('generalize-dec-fixed');
            }

        }, 20);
    });

    function repeat_sign(scroll){
        var MODEL_INDEX = 0;
        if(scroll < 690){
            return $('.model-animate').removeClass('active');
        }else if(690 <= scroll && scroll < 1037){
            MODEL_INDEX = 1
            console.log(1, scroll)
        }else if(1400 <= scroll && scroll < 1744){
            MODEL_INDEX = 2
            console.log(2, scroll)
        }else if(2100 <= scroll && scroll < 2455){
            MODEL_INDEX = 3
            console.log(3, scroll)
        }else if(2807 <= scroll && scroll < 3167){
            MODEL_INDEX = 4
            console.log(4, scroll)
        }else if(3526 <= scroll && scroll < 3800){
            MODEL_INDEX = 5
            console.log(5, scroll)
        }
        $('.generalize-explain-title-'+ MODEL_INDEX).fadeIn().siblings('.generalize-explain-title-pub').hide();
        $('.generalize-explain-content-'+ MODEL_INDEX).fadeIn().siblings('.generalize-explain-content-pub').hide()

    }

});