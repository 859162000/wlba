

require(['jquery'], function( $ ) {

  $('.area-active-list').mouseenter(function(){
    $(this).find('.area-ac-mask').stop(false, true).fadeIn(200);
      console.log(1)
  }).mouseleave(function(){
    $(this).find('.area-ac-mask').stop(false, true).fadeOut(200);
  })

  $('#area-nav li').on( 'click', function(){
    var index = $(this).index();
    $(this).addClass('active').siblings().removeClass('active')
    $('.active_slide').animate({
      left: 155* index
    },300)
  })

});