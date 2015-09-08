(function() {
  require.config({
    paths: {
        jquery: 'lib/jquery.min',
        'jquery.animateNumber': 'lib/jquery.animateNumber.min'
    },
    shim: {
        'jquery.animateNumber': ['jquery']
    }
  });

  require(['jquery','jquery.animateNumber'], function($){
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
    var $num = $('.num-space');
    var is_animate = true;
    $.ajax({
        url: '/api/gettopofearings/',
        type: "POST"
    }).done(function (json) {
        var rankingList_phone = [];
        var rankingList_amount = [];
        var json_one;
        for(var i=0; i<json.records.length; i++){
            json_one = json.records[i];
            if(json_one!=''){
                if(i<=2){
                    rankingList_phone.push(['<li class="front">'+json_one.phone+'</li>'].join(''));
                    rankingList_amount.push(['<li class="front num-animate">'+json_one.amount+'</li>'].join(''));
                }else{
                    rankingList_phone.push(['<li>'+json_one.phone+'</li>'].join(''));
                    rankingList_amount.push(['<li class="num-animate">'+json_one.amount+'</li>'].join(''));
                }
            }else{
                rankingList_phone.push(['<li>虚位以待</li>'].join(''));
                rankingList_amount.push(['<li>虚位以待</li>'].join(''));
            }

        }
        $('.rankingList ul.two').html(rankingList_phone.join(''));
        $('.rankingList ul.three').html(rankingList_amount.join(''));

        $(window).scroll(function(){
            if($(window).scrollTop()>=300&&is_animate){
                $('.num-animate').each(function(){
                    var key = parseInt($(this).html());
                    $(this).prop('number', 0).animateNumber({
                      number: key,
                    },1000);
                    is_animate = false;
                })
            }
        });


       })
    })

}).call(this);



