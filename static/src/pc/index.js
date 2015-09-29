require.config({
  paths: {
    'jquery.animateNumber': 'lib/jquery.animateNumber.min',
    'countdown' : 'model/countdown'
  },
  shim: {
    'jquery.animateNumber': ['jquery'],
    'jquery.modal': ['jquery']
  }
});

require(['jquery', 'jquery.animateNumber', 'countdown'], function( $ ) {

  //number adminante
  var $num = $('.num-space')
  $num.each(function( ) {
    var amount = parseInt($(this).attr('data-number')).toString(),
        type = $(this).attr('data-type');
    $(this).append(amountGe(amount, type));
  })
  function amountGe(value, type){
    var len = value.length, str = '';
    reType = type == 'man' ? '人' : '元';
    if(len > 8){
      str = isNode(value.substr(0,len-8), '亿') + isNode(value.substr(-8,4), '万');
    }else{
      str = isNode(value.substr(0,len-4), '万');
    }
    function isNode(substr, text){
      if(parseInt(substr) > 0){
        return " <span class='num-animate'>" + parseInt(substr) + "</span> <span class='num-text'>" + text + '</span>';
      }
      return '';
    }
    return str
  }
  $('.num-animate').each(function(){
    var key = parseInt($(this).html());
    $(this).prop('number', 0).animateNumber({
      number: key,
    },1000);
  })


  //倒计时
  var
    time = $('.recommend_time').attr('data-update'),
    endTime= new Date(time.replace(/-/g,"/"));
  $('.recommend_time').countdown(endTime);

  //nav fixed
  var $nav = $('.g-nav-warp');
  $(window).scroll(function(){
    $(window).scrollTop() > 80 ? $nav.addClass('g-nav-fixed').animate({'top': 0}, 300) : $nav.stop(!0,!0).removeClass('g-nav-fixed').removeAttr('style');
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
  ~function _initPart($partner, $next, $last, idx, count){
    $partner.css({'width': $partner.find('li').length * 100 + '%'})
    $next.on('click',function(){
      idx++
      if(idx > count) idx = 0;
      _amt(idx);
    })

    $last.on('click',function(){
      idx--
      if(idx < 0) idx = count;
      _amt(idx);
    })

    function _amt(page){
      $partner.animate({'left': - page * 1050}, 200)
    }
  }(
    $('.cn-ul-warp ul'),
    $('.cn-next'),
    $('.cn-last'),
    0,
    $('.cn-ul-warp li').length - 1
  );

  //扫描送红包
  $(window).scroll(function () {
      var $scroll = $(document).scrollTop();
      if($scroll > ($(document).height()*0.4)) {
        $('.bonus-icon').css({'top': '30%'})
      }else{
        $('.bonus-icon').css({'top': '60%'})
      }
  });
  $('.bonus-icon').on('click',function(){
    $('.bonus-img,.page').show();
  });
  $('.close').on('click',function(){
    $('.bonus-img,.page').hide();
  })
  function wxShareIcon(){
    var docleft = document.body.clientWidth;
    var left = (docleft - $('.i-mod-exhibition').width())/2 + $('.i-mod-exhibition').width();
    $('.bonus-icon').css({'left':left})
  }
  wxShareIcon()
  window.onresize = function(){
      wxShareIcon();
  };
});