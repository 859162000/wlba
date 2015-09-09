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
    var is_animate = true;
    function fmoney(s, type) {
        if (/[^0-9\.]/.test(s))
            return "0";
        if (s == null || s == "")
            return "0";
        s = s.toString().replace(/^(\d*)$/, "$1.");
        s = (s + "00").replace(/(\d*\.\d\d)\d*/, "$1");
        s = s.replace(".", ",");
        var re = /(\d)(\d{3},)/;
        while (re.test(s))
            s = s.replace(re, "$1,$2");
        s = s.replace(/,(\d\d)$/, ".$1");
        if (type == 0) {// 不带小数位(默认是有小数位)
            var a = s.split(".");
            if (a[1] == "00") {
                s = a[0];
            }
        }
        return s;
    }
    function page_scroll(){
        if($(window).scrollTop()>=200&&is_animate){
            $('.num-animate').each(function(){
                var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',')
                var key = parseInt($(this).attr('data-num'));
                $(this).prop('number', 0).animateNumber({
                    number: key,
                    numberStep: comma_separator_number_step
                },1000);
                is_animate = false;
            })
        }
    }

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
                var number = fmoney(json_one.amount, 0);
                if(i<=2){
                    rankingList_phone.push(['<li class="front">'+json_one.phone+'</li>'].join(''));
                    rankingList_amount.push(['<li class="front"><span class="num-animate" data-num="'+json_one.amount+'">0</span> 元</li>'].join(''));
                }else{
                    rankingList_phone.push(['<li>'+json_one.phone+'</li>'].join(''));
                    rankingList_amount.push(['<li><span class="num-animate" data-num="'+json_one.amount+'">0</span> 元</li>'].join(''));
                }

            }else{
                rankingList_phone.push(['<li>虚位以待</li>'].join(''));
                rankingList_amount.push(['<li>虚位以待</li>'].join(''));
            }

        }
        $('.rankingList ul.two').html(rankingList_phone.join(''));
        $('.rankingList ul.three').html(rankingList_amount.join(''));
        page_scroll();
        $(window).scroll(function(){
            page_scroll();
        });
       })
    })
}).call(this);



