$(function(){
     var sixlis = document.getElementById("six_lis"),
         audio = document.getElementById("audios"),
         audiobtn = document.getElementById("audio");
     var ss = 1;
     $('#sec').fullpage();
     sixlis.addEventListener("touchstart",function(){
          $(this).next().slideToggle();
      },false)
     audiobtn.addEventListener("click",function(){
          if(ss == 1){
              $(this).addClass("audio_off");
              audio.pause();
              ss = 2;
          }else{
              audio.play();
              $(this).removeClass("audio_off");
              ss = 1;
          }
     },false)
});


