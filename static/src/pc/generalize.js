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
        $('.generalize-explain-title-'+ ele_id).fadeIn().siblings('.generalize-explain-title-pub').hide();
        $('.generalize-explain-content-'+ ele_id).fadeIn().siblings('.generalize-explain-content-pub').hide()
    }, {
      offset: -100
    })

    var
        $download_layout = $('.generalize-dec-pub'),
        $download_layout_copy = $('.generalize-dec-other'),
        $download_layout_RIGHT =$(window).width()- $download_layout.offset().left- $download_layout.width(),
        $download_layout_TOP = 965;

    $(window).scroll(function () {
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
    })

});