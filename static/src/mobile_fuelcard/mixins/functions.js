export const ajax = function (options) {
    $.ajax({
        url: options.url,
        type: options.type,
        data: options.data,
        dataType: options.dataType,
        async: options.async || true,
        beforeSend (xhr, settings) {
            options.beforeSend && options.beforeSend(xhr);
            //django配置post请求
            if (!_csrfSafeMethod(settings.type) && _sameOrigin(settings.url)) {
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            }
        },
        success (data) {
            options.success && options.success(data);
        },
        error (xhr) {
            options.error && options.error(xhr);
        },
        complete () {
            options.complete && options.complete();
        }
    });
};

export const signView = function (sign) {
    $('.error-sign').html(sign).removeClass('moveDown').addClass('moveDown').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
        $(this).removeClass('moveDown');
    });
}

export const getCookie = function (name) {
    let cookie, cookies, i, cookieValue = null;
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
};

const _csrfSafeMethod = (method) => {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
};

const _sameOrigin = function (url) {
    let host, origin, protocol, sr_origin;
    host = document.location.host;
    protocol = document.location.protocol;
    sr_origin = '//' + host;
    origin = protocol + sr_origin;
    return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
};





