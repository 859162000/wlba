/**
 * 封装的ajax，置入了csrf
 * @param options
 */

export const ajax = (options) => {
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

/**
 * getCookie
 * 获取浏览器cookie
 *
 */

export const getCookie = (name) => {
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

/**
 * 获取url参数值
 */
export const getQueryStringByName = (name) => {
    const result = location.search.match(new RegExp('[\?\&]' + name + '=([^\&]+)', 'i'));
    if (result == null || result.length < 1) {
        return '';
    }
    return result[1];
}



const _csrfSafeMethod = (method) => {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
};

const _sameOrigin = (url) => {
    let host, origin, protocol, sr_origin;
    host = document.location.host;
    protocol = document.location.protocol;
    sr_origin = '//' + host;
    origin = protocol + sr_origin;
    return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
};

/**
 * 计算器
 */
export const calculate = (() => {

    const _calculate = function (amount, rate, period, pay_method) {
        var divisor, rate_pow, result, term_amount, month_rate;
        if (/等额本息/ig.test(pay_method)) {
            month_rate = rate / 12
            rate_pow = Math.pow(1 + month_rate, period)
            term_amount = amount * (month_rate * rate_pow) / (rate_pow-1)
            term_amount = term_amount.toFixed(2)
            result  = (term_amount * period - amount).toFixed(2)
        } else if (/日计息/ig.test(pay_method)) {
            result = amount * rate * period / 360;
        } else {
            result = amount * rate * period / 12;
        }
        return Math.floor(result * 100) / 100;
    };

    function operation(dom, callback) {
        let earning, earning_element, earning_elements, fee_earning;

        let target = dom,
            existing = parseFloat(target.attr('data-existing')),
            period = target.attr('data-period'),
            rate = target.attr('data-rate') / 100,
            pay_method = target.attr('data-paymethod'),
            activity_rate = target.attr('activity-rate') / 100,
            activity_jiaxi = target.attr('activity-jiaxi') / 100,
            amount = parseFloat(target.val()) || 0;

        if (amount > target.attr('data-max')) {
            amount = target.attr('data-max');
            target.val(amount);
        }
        activity_rate += activity_jiaxi;
        amount = parseFloat(existing) + parseFloat(amount);
        earning = _calculate(amount, rate, period, pay_method);
        fee_earning = _calculate(amount, activity_rate, period, pay_method);

        if (earning < 0) {
            earning = 0;
        }
        earning_elements = (target.attr('data-target')).split(',');

        for (let i = 0; i < earning_elements.length; i++) {
            earning_element = earning_elements[i];
            if (earning) {
                fee_earning = fee_earning ? fee_earning : 0;
                earning += fee_earning;
                $(earning_element).text(earning.toFixed(2));
            } else {
                $(earning_element).text("0.00");
            }
        }
        callback && callback();
    }

    return {
        operation : operation
    }
})()





