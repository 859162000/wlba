webpackJsonp([3],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _api = __webpack_require__(3);

	(function () {
	    /**
	     * 公司信息tab
	     */
	    $('.toggleTab').on('click', function () {
	        $(this).siblings().toggle();
	        $(this).find('span').toggleClass('icon-rotate');
	    });

	    /**
	     * 倒计时
	     */
	    var countDown = $('#countDown');

	    var countDown_func = function countDown_func(target) {
	        var endTimeList = target.attr('data-left').replace(/-/g, '/');
	        var TimeTo = function TimeTo(dd) {
	            var t = new Date(dd),
	                n = parseInt(new Date().getTime()),
	                c = t - n;
	            if (c <= 0) {
	                target.text('活动已结束');
	                clearInterval(window['interval']);
	                return;
	            }
	            var ds = 60 * 60 * 24 * 1000,
	                d = parseInt(c / ds),
	                h = parseInt((c - d * ds) / (3600 * 1000)),
	                m = parseInt((c - d * ds - h * 3600 * 1000) / (60 * 1000)),
	                s = parseInt((c - d * ds - h * 3600 * 1000 - m * 60 * 1000) / 1000);
	            m < 10 ? m = '0' + m : '';
	            s < 10 ? s = '0' + s : '';
	            target.text(d + '天' + h + '小时' + m + '分' + s + '秒');
	        };
	        window['interval'] = setInterval(function () {
	            TimeTo(endTimeList);
	        }, 1000);
	    };
	    countDown.length > 0 && countDown_func(countDown);

	    /**
	     * 动画
	     */

	    $(function () {
	        var $progress = $('.progress-percent');
	        setTimeout(function () {
	            var percent = parseFloat($progress.attr('data-percent'));
	            if (percent == 100) {
	                $progress.css('margin-top', '-10%');
	            } else {
	                $progress.css('margin-top', 100 - percent + '%');
	            }
	            setTimeout(function () {
	                $progress.addClass('progress-bolang');
	            }, 1000);
	        }, 300);
	    });
	    /**
	     * 微信分享自定义
	     */
	    var weixin_share = function weixin_share() {
	        var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ'];
	        (0, _api.ajax)({
	            type: 'GET',
	            url: lib.weiURL,
	            dataType: 'json',
	            success: function success(data) {
	                //请求成功，通过config注入配置信息,
	                wx.config({
	                    debug: false,
	                    appId: data.appId,
	                    timestamp: data.timestamp,
	                    nonceStr: data.nonceStr,
	                    signature: data.signature,
	                    jsApiList: jsApiList
	                });
	            }
	        });
	        wx.ready(function () {
	            var $productName = $('.product-name'),
	                $earningRate = $('.profit-txt'),
	                $period = $('.time-txt');

	            var host = 'https://www.wanglibao.com',
	                shareName = $productName.attr('data-name'),
	                shareImg = host + '/static/imgs/mobile/share_logo.png',
	                shareLink = host + '/weixin/detail/' + $productName.attr('data-productID'),
	                shareMainTit = '我在网利宝发现一个不错的投资标的，快来看看吧',
	                shareBody = shareName + ',年收益' + $earningRate.attr('data-earn') + '%,期限' + $period.attr('data-period');
	            //分享给微信好友
	            wx.onMenuShareAppMessage({
	                title: shareMainTit,
	                desc: shareBody,
	                link: shareLink,
	                imgUrl: shareImg
	            });
	            //分享给微信朋友圈
	            wx.onMenuShareTimeline({
	                title: shareMainTit,
	                link: shareLink,
	                imgUrl: shareImg
	            });
	            //分享给QQ
	            wx.onMenuShareQQ({
	                title: shareMainTit,
	                desc: shareBody,
	                link: shareLink,
	                imgUrl: shareImg
	            });
	        });
	    };
	    weixin_share();
	})();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },
/* 1 */,
/* 2 */,
/* 3 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	/**
	 * 封装的ajax，置入了csrf
	 * @param options
	 */

	var ajax = exports.ajax = function ajax(options) {
	    $.ajax({
	        url: options.url,
	        type: options.type,
	        data: options.data,
	        dataType: options.dataType,
	        async: options.async || true,
	        beforeSend: function beforeSend(xhr, settings) {
	            options.beforeSend && options.beforeSend(xhr);
	            //django配置post请求
	            if (!_csrfSafeMethod(settings.type) && _sameOrigin(settings.url)) {
	                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
	            }
	        },
	        success: function success(data) {
	            options.success && options.success(data);
	        },
	        error: function error(xhr) {
	            options.error && options.error(xhr);
	        },
	        complete: function complete() {
	            options.complete && options.complete();
	        }
	    });
	};

	/**
	 * getCookie
	 * 获取浏览器cookie
	 *
	 */

	var getCookie = exports.getCookie = function getCookie(name) {
	    var cookie = undefined,
	        cookies = undefined,
	        i = undefined,
	        cookieValue = null;
	    if (document.cookie && document.cookie !== '') {
	        cookies = document.cookie.split(';');
	        i = 0;
	        while (i < cookies.length) {
	            cookie = $.trim(cookies[i]);
	            if (cookie.substring(0, name.length + 1) === name + '=') {
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
	var getQueryStringByName = exports.getQueryStringByName = function getQueryStringByName(name) {
	    var result = location.search.match(new RegExp('[\?\&]' + name + '=([^\&]+)', 'i'));
	    if (result == null || result.length < 1) {
	        return '';
	    }
	    return result[1];
	};

	var _csrfSafeMethod = function _csrfSafeMethod(method) {
	    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
	    );
	};

	var _sameOrigin = function _sameOrigin(url) {
	    var host = undefined,
	        origin = undefined,
	        protocol = undefined,
	        sr_origin = undefined;
	    host = document.location.host;
	    protocol = document.location.protocol;
	    sr_origin = '//' + host;
	    origin = protocol + sr_origin;
	    return url === origin || url.slice(0, origin.length + 1) === origin + '/' || url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/' || !/^(\/\/|http:|https:).*/.test(url);
	};

	/**
	 * 计算器
	 */
	var calculate = exports.calculate = function () {

	    var _calculate = function _calculate(amount, rate, period, pay_method) {
	        var divisor, rate_pow, result, term_amount, month_rate;
	        if (/等额本息/ig.test(pay_method)) {
	            month_rate = rate / 12;
	            rate_pow = Math.pow(1 + month_rate, period);
	            term_amount = amount * (month_rate * rate_pow) / (rate_pow - 1);
	            term_amount = term_amount.toFixed(2);
	            result = (term_amount * period - amount).toFixed(2);
	        } else if (/日计息/ig.test(pay_method)) {
	            result = amount * rate * period / 360;
	        } else {
	            result = amount * rate * period / 12;
	        }
	        return Math.floor(result * 100) / 100;
	    };

	    function operation(dom, callback) {
	        var earning = undefined,
	            earning_element = undefined,
	            earning_elements = undefined,
	            fee_earning = undefined;

	        var target = dom,
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
	        earning_elements = target.attr('data-target').split(',');

	        for (var i = 0; i < earning_elements.length; i++) {
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
	        operation: operation
	    };
	}();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);