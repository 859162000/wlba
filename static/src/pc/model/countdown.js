

 define(['jquery'], function ($) {
   $.fn.countdown = function(endTimt){
     var
       self = $(this),
       dateTimer = null,
       first = true,
       str = '',
       t= 0,
       h = 0,
       m = 0,
       s = 0;
      function callback(){
        var startTime = new Date();
        t = endTimt.getTime() - startTime.getTime();
        if(t > 0){
          h = Math.floor(t/1000/60/60%24);
          m = Math.floor(t/1000/60%60);
          s = Math.floor(t/1000%60);
        }else if (t == 0){
          clearInterval(dateTimer)
        }
        str = "距离下场更新：" + h + " 时 " + m + " 分 " + s + " 秒 ";
        self.html(str)
        if(first){
          self.addClass('animated fadeInDown')
          first = false;
        }
      }
      dateTimer = setInterval(callback, 1000);
   }
 });