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
        console.log(ele_id)
        var model_class = $(this.element).attr('class');
        if(model_class.indexOf("active") < 0){
            ele.addClass('active');
        }
        $('.generalize-explain-title-'+ ele_id).fadeIn().siblings('.generalize-explain-title-pub').hide()
        $('.generalize-explain-content-'+ ele_id).fadeIn().siblings('.generalize-explain-content-pub').hide()
    }, {
      offset: -60
    })


    var ele_right =$(window).width()- $('.generalize-dec').offset().left- $('.generalize-dec').width()
    var ele_top = 965;
    $(window).scroll(function () {
        if($(window).scrollTop() > ele_top){
            $(".generalize-dec").addClass('generalize-dec-fixed').css('right', ele_right).animate({top: 100}, 300)
        }else if($(window).scrollTop() < ele_top){
            $(".generalize-dec").stop(!0, !0).removeAttr('style').removeClass('generalize-dec-fixed');
        }

    })

});