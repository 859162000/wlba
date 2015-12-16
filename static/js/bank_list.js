;(function(){
    require.config({
        paths: {
          jquery: 'lib/jquery.min'
        }
    });
    require(['jquery'], function($) {
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
        $.ajax({
            url: '/api/pay/the_one_card/',
            data: {},
            type: 'GET',
            success: function (data) {
<<<<<<< HEAD
                var strHtml = '<div class="w100 clearfix">'
                strHtml+='<div class="bank-card">'
                     +'<div class="bank-card--title-bar row">';
                if(data.bank.name.length > 14) {
                  strHtml += '<div class="bank-card--bank-name"><label title="' + data.bank.name + '" class="bankname">' + data.bank.name + '</label>';
                }else{
                  strHtml += '<div class="bank-card--bank-name span9"><label>' + data.bank.name +'</label>';
                }
                strHtml +='<span class="bindingEd">已绑定</span>'
                     +'</div><div class="bank-card--icon span3-omega"><img src="/static/images/bank_card.png">'
                     +'</div></div><div class="row"><dl class="bank-card--info-row">'
                     +'<dt class="bank-card--info-title">账号</dt>'
                     +'<dd class="bank-card--info-value">'+ data.no.substring(0,3)+'**** ****' +data.no.substr(data.no.length-4)+'</dd>'
                     +'</dl></div></div></div>';
                $('#add-card-button').before(strHtml)
                $('#add-card-button').hide()
            },
            error : function(){
                $('#add-card-button').show()
=======

            },
            error : function(){
>>>>>>> 同卡进出
                $.ajax({
                    url: '/api/pay/cnp/list_new/',
                    data: {},
                    type: 'POST',
                    success: function (data) {
                        if(data.cards.length > 0){
                            var strHtml = ''
                            $.each(data.cards,function(i,o){
                              strHtml+='<div class="bank-card">'
                                     +'<div class="bank-card--title-bar row">';
                              if(o.bank_name.length > 14) {
                                  strHtml += '<div class="bank-card--bank-name"><label title="' + o.bank_name + '" class="bankname">' + o.bank_name + '</label>';
                              }else{
                                  strHtml += '<div class="bank-card--bank-name span9"><label>' + o.bank_name +'</label>';
                              }
                              strHtml+='<span>待绑定</span>'
                                     +'</div><div class="bank-card--icon span3-omega"><img src="/static/images/bank_card.png">'
                                     +'</div></div><div class="row"><dl class="bank-card--info-row">'
                                     +'<dt class="bank-card--info-title">账号</dt>'
                                     +'<dd class="bank-card--info-value">'+ o.storable_no.substring(0,3)+'**** ****' +o.storable_no.substr(o.storable_no.length-4)+'</dd>'
                                     +'</dl></div><div data-card="'+ o.storable_no +'" class="binding-card">绑定该卡</div></div>';
                            })
                            $('#add-card-button').before(strHtml)
                        }
                    }
                });
            }
        });
    })
})()