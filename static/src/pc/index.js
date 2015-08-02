
require.config({
  paths: {
    'jquery.animateNumber': 'lib/jquery.animateNumber.min'
  },
  shim: {
    'jquery.animateNumber': ['jquery']
  }
});

require(['jquery', 'jquery.animateNumber'], function( $ ) {

  //number adminante
  $('.num-animate').prop('number', 0).animateNumber({
    number: 5000,
  },2000);


  //nav fixed
  var $nav = $('.g-nav-warp');
  $(window).scroll(function(){
    $(window).scrollTop() > 400 ? $nav.addClass('g-nav-fixed').animate({'top': 0}, 200) : $nav.stop(!0,!0).removeClass('g-nav-fixed').animate({'top': -80}, 20);
  })

  //banner
  var currentBanner = 0, timer = null, speedBanner = 3000,
  banners = $('.slide-banner'),
  bannerCount = banners.length,
  anchors = $('.slide-anchor');
  switchBanner = function() {
    $(banners[currentBanner]).fadeOut();
    $(anchors[currentBanner]).toggleClass('active');
    currentBanner = (currentBanner + 1) % bannerCount;
    $(banners[currentBanner]).fadeIn();
    $(anchors[currentBanner]).toggleClass('active');
  };
  timer = setInterval(switchBanner, speedBanner);
  anchors.mouseover(function(e) {
    return clearInterval(timer);
  }).mouseout(function(e) {
    return timer = setInterval(switchBanner, speedBanner);
  });
  anchors.click(function(e) {
    e.preventDefault();
    var index = $(this).index();
    if (index !== currentBanner) {
      $(banners[currentBanner]).fadeOut();
      $(anchors[currentBanner]).toggleClass('active');
      $(banners[index]).fadeIn();
      $(anchors[index]).toggleClass('active');
      return currentBanner = index;
    }
  });
  //余额显示
  var $balanceHide = $('.icon-eye03'),
      $balanceShow = $('.icon-eye02'),
      $balanceShowCont = $(".landed-cont-show"),
      $balanceHideCont = $(".landed-cont-hide");
  $balanceHide.on('click',function(){
    $balanceHide.hide()
    $balanceShow.show()
    $balanceHideCont.hide()
    $balanceShowCont.show()
  });
  $balanceShow.on('click',function(){
    $balanceShow.hide()
    $balanceHide.show()
    $balanceHideCont.show()
    $balanceShowCont.hide()
  })


  //合作伙伴
  var $partner= $('.cn-ul-warp ul'),
      partnership_H  = $partner.height(),
      $next = $('.cn-next'),
      $last = $('.cn-last'),
      currentHeight = 170,
      currentPartner = 0,
      speedParner = 100,
      partenrCount = Math.ceil(partnership_H / currentHeight);

  $next.on('click',function(){
    if(currentPartner === partenrCount-1) return
    currentPartner++
    $partner.animate({'top': - currentPartner * currentHeight}, speedParner, function(){
      if(currentPartner === partenrCount-1){
        $next.addClass('un-click');
        $last.removeClass('un-click');
      }
    })
  })
  $last.on('click',function(){
    if(currentPartner === 0) return
    currentPartner--
    $partner.animate({'top': currentPartner * currentHeight}, speedParner, function(){
      if(currentPartner === 0){
        $next.removeClass('un-click');
        $last.addClass('un-click');
      }
    })
  })

});