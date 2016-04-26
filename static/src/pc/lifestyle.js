/**
 * Created by caoyujiao on 16-2-1.
 */
var video_1 = document.getElementById('really-cool-video'),
    video_2 = document.getElementById('really-cool-video2');
// 原生的JavaScript事件绑定函数
  function bindEvent(ele, eventName, func){
      if(window.addEventListener){
          ele.addEventListener(eventName, func);
      }
      else{
          ele.attachEvent('on' + eventName, func);
      }
  }

   bindEvent(video_1,'ended',function(){
     document.getElementsByClassName('vjs-poster')[0].style.display='block';
     document.getElementsByClassName('vjs-big-play-button')[0].style.display='block';
     video_1.currentTime = 0;
   });

   bindEvent(video_1,'play',function(){
      document.getElementsByClassName('vjs-poster')[0].style.display='none';
      document.getElementsByClassName('vjs-big-play-button')[0].style.display='none';
   });

   bindEvent(video_2,'ended',function(){
      document.getElementsByClassName('vjs-poster')[1].style.display='block';
      document.getElementsByClassName('vjs-big-play-button')[1].style.display='block';
      video_2.currentTime = 0;
    });

   bindEvent(video_2,'play',function(){
      document.getElementsByClassName('vjs-poster')[1].style.display='none';
      document.getElementsByClassName('vjs-big-play-button')[1].style.display='none';
   });
require.config({
  paths: {
    'videojs': 'lib/video.min'
  }
});
require(['jquery','videojs'], function($, videojs) {

    //tab
    $("li.tab-item").on("mouseenter", function(){
        var self = $(this),
            tp = self.parents("div.part-item"),
            inx = self.index();
        if(self.hasClass("active")){
            return;
        }else{
            self.addClass("active").siblings("li.tab-item").removeClass("active");
            tp.find("div.cont-item").removeClass("active").eq(inx).addClass("active");
        }
    });
});