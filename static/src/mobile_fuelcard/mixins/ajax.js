
export function ajax(){
    $.ajax({
        url: options.url,
        type: options.type,
        data: options.data,
        dataType : options.dataType,
        beforeSend: function(xhr, settings) {
            options.beforeSend && options.beforeSend(xhr);
            //django配置post请求
            if (!lib._csrfSafeMethod(settings.type) && lib._sameOrigin(settings.url)) {
              xhr.setRequestHeader('X-CSRFToken', lib._getCookie('csrftoken'));
            }
        },
        success:function(data){
            options.success && options.success(data);
        },
        error: function (xhr) {
            options.error && options.error(xhr);
        },
        complete:function(){
            options.complete && options.complete();
        }
    });

    let _getCookie = (name) -> {

    }

}

    var lib = {

        _getCookie :function(name){
            var cookie, cookieValue, cookies, i;
                cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    cookies = document.cookie.split(';');
                    i = 0;
                    while (i < cookies.length) {
                      cookie = $.trim(cookies[i]);
                      if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                      }
                      i++;
                    }
                }
              return cookieValue;
        },
        _csrfSafeMethod :function(method){
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        },
        _sameOrigin:function(url){
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = '//' + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
        }
    }
    return {
        ajax                   : lib._ajax,
        getCookie              : lib._getCookie,
        csrfSafeMethod         : lib._csrfSafeMethod,
        sameOrigin             : lib._sameOrigin,
    }
