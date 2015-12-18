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
    /*领取体验金*/
      $('.no_invest').on('click',function(){
          $.ajax({
            url: '/api/experience/get_experience/',
            type: "POST",
            data: {}
         }).done(function (xhr) {
            if(xhr.ret_code == 0){
                $('#receiveSuccess').modal();
                var par = $('#receiveSuccess');
                var tyjye = fmoney((parseFloat($('.tyjye').text())+xhr.data.amount),2);
                var zzc = fmoney((parseFloat($('.zzc').text())+xhr.data.amount),2);
                var rzje = fmoney(xhr.data.amount,2,1);
                par.find('.close-modal').hide();
                par.find('.money_count').html(xhr.data.amount+'<span>元</span>');
                par.find('.money_counts').text(rzje+'元体验金')
                $('.tyjye').text(tyjye);
                $('.zzc').text(zzc);
                $('.rzje').text(rzje+'元');
                $('.invest_ed').removeClass('invest_ed').addClass('investBtn');
                $('.no_invest').removeClass('no_invest').addClass('draw_btn_ed').text('已领取体验金'+ xhr.data.amount  +'元');
            }else{
                tool.modalAlert({ title: '温馨提示', msg: '<p>体验金由系统自动发放，</p><p>请继续关注网利宝最新活动。</p>'})
            }
         })
      })
      /*老用户*/
      $('.invested').on('click',function(){
          $('#oldUser').modal()
      })
      /*投标*/
      $('.project_right').delegate('.investBtn','click',function() {
         $.ajax({
            url: '/api/experience/buy/',
            type: "POST",
            data: {}
         }).done(function (xhr) {
            if(xhr.data.ret_code > 0){
                return tool.modalAlert({
                    title: '温馨提示',
                    msg: xhr.data.message
                });
            }else{
                $('#success').modal()
                $('#success').find('.close-modal').hide()
                setInterval(function(){
                    $.modal.close()
                    /*$('.investBtn').text('已投资'+ xhr.data.amount +'元').addClass('invest_ed').removeClass('investBtn')
                    $('.income_fonts').show().text('将于'+ xhr.data.term_date +'收益'+ xhr.data.interest +'元')*/
                    location.reload();
                },2000)
            }
         }).fail(function(xhr){
            return tool.modalAlert({
              title: '温馨提示',
              msg: xhr.data.message
            });
         })
      })
      /*展开更多*/
      $('.more_btn').on('click',function(){
        $('.project_list').slideToggle()
      })
      /*关闭弹框*/
      $('#closeBtn').on('click',function(){
        $.modal.close()
      })
      /*去投资按钮下滑*/
      $('#goBtn').on('click',function(){
        $.modal.close()
        $('body,html').animate({scrollTop: $('.experience_project').offset().top}, 600);
      })
      /*格式化金额*/
        function fmoney(s, n, m)
        {
           n = n > 0 && n <= 20 ? n : 2;
           s = parseFloat((s + "").replace(/[^\d\.-]/g, "")).toFixed(n) + "";
           var l = s.split(".")[0].split("").reverse(),
           r = s.split(".")[1];
           console.dir(m +'dddddddd' + r)
           t = "";
           for(i = 0; i < l.length; i ++ )
           {
              t += l[i] + ((i + 1) % 3 == 0 && (i + 1) != l.length ? "," : "");
           }
           if(m == 1 && r == '00')
           {
               return t.split("").reverse().join("");
           }else{
               return t.split("").reverse().join("") + "." + r;
           }

        }
  });
}).call(this);