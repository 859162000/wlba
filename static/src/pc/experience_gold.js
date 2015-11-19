(function() {
  require.config({
    paths: {
        jquery: 'lib/jquery.min',
        'jquery.modal': 'lib/jquery.modal.min',
        tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
  });

  require(['jquery',"tools"], function($,tool) {
    var  csrfSafeMethod, getCookie,sameOrigin,
    getCookie = function(name) {
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
    csrfSafeMethod = function(method) {
        return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
    };
    sameOrigin = function(url) {
        var host, origin, protocol, sr_origin;
        host = document.location.host;
        protocol = document.location.protocol;
        sr_origin = "//" + host;
        origin = protocol + sr_origin;
        return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
    };
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
              xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }
    });

      $('.no_invest').on('click',function(){
          $.ajax({
            url: '/api/experience/get_experience/',
            type: "POST",
            data: {}
         }).done(function (xhr) {
            if(xhr.ret_code == 0){
                var par = $('#receiveSuccess');
                $('#receiveSuccess').modal()
                par.find('.close-modal').hide()
                par.find('.money_count').text(xhr.data.amount)
                par.find('.money_counts').text(xhr.data.amount+'元体验金')
                $('.tyjye').text(parseFloat($('.tyjye').text())+xhr.data.amount)
                $('.zzc').text(parseFloat($('.zzc').text())+xhr.data.amount)
                $('.rzje').text(xhr.data.amount+'元')
                $('.invest_ed').removeClass('invest_ed').addClass('investBtn');
            }
         })
      })
      $('.invested').on('click',function(){
          $('#oldUser').modal()
      })
      $('.project_right').delegate('.investBtn','click',function() {
         $.ajax({
            url: '/api/experience/buy/',
            type: "POST",
            data: {}
         }).done(function (xhr) {
            $('#success').modal()
            $('#success').find('.close-modal').hide()
            setInterval(function(){
                $.modal.close()
                $('.investBtn').text('已投资'+ xhr.data.amount +'元').addClass('invest_ed').removeClass('investBtn')
                $('.income_fonts').show().text('将于'+ xhr.data.term_date +'收益'+ xhr.data.interest +'元')
            },2000)
         })
      })
      $('.more_btn').on('click',function(){
        $('.project_list').slideToggle()
      })
      $('#closeBtn').on('click',function(){
        $.modal.close()
      })
      $('#goBtn').on('click',function(){
        $.modal.close()
        $('body,html').animate({scrollTop: $('.experience_project').offset().top}, 600);
      })
  });
}).call(this);