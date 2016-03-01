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
        var model_class = $(this.element).attr('class');
        if(model_class.indexOf("active") < 0){
            ele.addClass('active').siblings('.model-animate').removeClass('active');
        }
        $('.generalize-explain-title-'+ ele_id).fadeIn().siblings('.generalize-explain-title-pub').hide()
        $('.generalize-explain-content-'+ ele_id).fadeIn().siblings('.generalize-explain-content-pub').hide()
    }, {
      offset: -100
    })
    var ele_right =$(window).width()- $('.generalize-dec-pub').offset().left- $('.generalize-dec-pub').width()
    var ele_top = 965;
    $(window).scroll(function () {
        console.log($(window).scrollTop())
        if($(window).scrollTop() > ele_top){
                if($(window).scrollTop() > 3768){
                    $(".generalize-dec-pub").hide()
                    return $(".generalize-dec-other").show()
                }else{
                    $(".generalize-dec-pub").show()
                     $(".generalize-dec-other").hide()
                }
                $(".generalize-dec-pub").addClass('generalize-dec-fixed').css('right', ele_right).animate({top: 150}, 300)

        }else if($(window).scrollTop() < ele_top){
            $(".generalize-dec-pub").stop(!0, !0).removeAttr('style').removeClass('generalize-dec-fixed');
        }
    })


});