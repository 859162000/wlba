(function() {
  require.config({
    paths: {
        jquery: '/static/src/pc/lib/jquery.min',
        'jquery.animateNumber': '/static/src/pc/lib/jquery.animateNumber.min'
    },
    shim: {
        'jquery.animateNumber': ['jquery']
    }
  });

  require(['jquery','jquery.animateNumber'], function($) {
      var csrfSafeMethod, getCookie, sameOrigin,
          getCookie = function (name) {
              var cookie, cookieValue, cookies, i;
              cookieValue = null;
              if (document.cookie && document.cookie !== "") {
                  cookies = document.cookie.split(";");
                  i = 0;
                  while (i < cookies.length) {
                      cookie = $.trim(cookies[i]);
                      if (cookie.substring(0, name.length + 1) === (name + "=")) {
                          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                          break;
                      }
                      i++;
                  }
              }
              return cookieValue;
          };
      csrfSafeMethod = function (method) {
          return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
      };
      sameOrigin = function (url) {
          var host, origin, protocol, sr_origin;
          host = document.location.host;
          protocol = document.location.protocol;
          sr_origin = "//" + host;
          origin = protocol + sr_origin;
          return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
      };
      $.ajaxSetup({
          beforeSend: function (xhr, settings) {
              if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                  xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
              }
          }
      });
      var is_animate = true;

      function page_scroll() {
          $('.num-animate').each(function () {
              var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',')
              var key = parseInt($(this).attr('data-num'));
              $(this).prop('number', 0).animateNumber({
                  number: key,
                  numberStep: comma_separator_number_step
              }, 1000);
              is_animate = false;
          })
      }

      $('#wrap,#loading').css({
          height: $(window).height()
      });

      $(window).on('resize',function(){
          $('#wrap,#loading').css({
              height: $(window).height()
          });
      });
      window.onload = function() {

      }

      var step = 0;
      step0();
      function step0(){
          var i=9;
          var timer1 = setInterval(function(){
              i--;
              if(i===0){
                  clearInterval(timer1);

              }
          },1000);
      }

      function boy_animate(){

      }

      var j=10;
      var timer2 = setInterval(function(){
          j--;
          if(j===0){
              clearInterval(timer2);
              step_wrap(step);
          }
      },1000);

      function step_wrap(step){
          switch (step){
              case 0:
                  choice1();
                  break;
              case 1:

                  break;
          }
      }

      function choice1(){
          $('.choice').fadeIn(500);
          $('.choice1').click(function(){
              $('.choice').fadeOut(500);
              $('.boy').removeClass('boy_animate1').addClass('boy_animate2');
          });
      }
  })

}).call(this);



