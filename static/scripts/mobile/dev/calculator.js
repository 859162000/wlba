webpackJsonp([0],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _api = __webpack_require__(2);

	var _ui = __webpack_require__(3);

	(function () {

	    var $inputCalculator = $('input[data-role=p2p-calculator]'),
	        $calculatorBuy = $('.calculator-buy'),
	        $countInput = $('.count-input');

	    var productId = void 0,
	        amount_profit = void 0,
	        amount = void 0;

	    $inputCalculator.on('input', function () {
	        _api.calculate.operation($(this));
	    });

	    $calculatorBuy.on('click', function () {
	        productId = $(this).attr('data-productid');
	        amount = $countInput.val();
	        amount_profit = $("#expected_income").text();
	        if (amount % 100 !== 0 || amount == '') {
	            return (0, _ui.signModel)("请输入100的整数倍???？");
	        } else {
	            window.location.href = '/weixin/view/buy/' + productId + '/?amount=' + amount;
	        }
	    });
	})();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },
/* 1 */,
/* 2 */
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
	    var cookie = void 0,
	        cookies = void 0,
	        i = void 0,
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
	    var host = void 0,
	        origin = void 0,
	        protocol = void 0,
	        sr_origin = void 0;
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
	        var rate_pow, result, term_amount, month_rate;
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
	        var earning = void 0,
	            earning_element = void 0,
	            earning_elements = void 0,
	            fee_earning = void 0;

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

/***/ },
/* 3 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	/**
	 *
	 * 引入fuel_alert.jade
	 * @param text 文字说明
	 * @param callback 回调函数
	 */
	window.alert = function (text, callback) {

	    var $alert = $('.wx-alert'),
	        $button = $('.wx-submit');

	    $alert.css('display', '-webkit-box').find('.wx-text').text(text);

	    $button.on('click', function () {
	        $alert.hide();
	        callback && callback();
	    });
	};

	/**
	 * 引入fuel_alert.jade
	 * @param title confim文字说明
	 * @param certainName 左边按钮文字
	 * @param callback  回调函数
	 * @param callbackData 回调函数的数据
	 */
	window.confirm = function (title) {
	    var certainName = arguments.length <= 1 || arguments[1] === undefined ? '确定' : arguments[1];
	    var callback = arguments.length <= 2 || arguments[2] === undefined ? null : arguments[2];
	    var callbackData = arguments.length <= 3 || arguments[3] === undefined ? null : arguments[3];

	    var $confirm = $('.confirm-warp');
	    if ($confirm.length <= 0) return;
	    $confirm.show();
	    $confirm.find('.confirm-text').text(title);
	    $confirm.find('.confirm-certain').text(certainName);

	    $confirm.find('.confirm-cancel').on('click', function () {
	        $confirm.hide();
	    });

	    $confirm.find('.confirm-certain').on('click', function () {
	        $confirm.hide();
	        if (callback) {
	            callbackData ? callback(callbackData) : callback();
	        }
	    });
	};

	var signModel = exports.signModel = function signModel(text) {
	    $('.error-sign').html(text).removeClass('moveDown').addClass('moveDown').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
	        $(this).removeClass('moveDown');
	    });
	};
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);