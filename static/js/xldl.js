/**
 * Created by rsj217 on 15-1-21.
 */
// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      'jquery': 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    var high=document.body.scrollHeight;
    //立即注册
    $('#top-zc').on('click',function(){
     pageScroll();
    });

    function pageScroll(){
      //把内容滚动指定的像素数
      window.scrollBy(0,-high);
      //获取scrollTop值
      var sTop=document.documentElement.scrollTop+document.body.scrollTop;
      //判断当页面到达顶部
      if(sTop==0) clearTimeout(scrolldelay);
    }

  });
}).call(this);
