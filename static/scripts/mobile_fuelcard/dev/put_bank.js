webpackJsonp([2],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _ui = __webpack_require__(2);

	var _functions = __webpack_require__(3);

	(function () {
	    var $setBank = $('.set-bank'),
	        $signItem = $('.set-bank-sign'),
	        $confirm = $('.bank-confirm');

	    var put_bank = function put_bank(id) {
	        (0, _functions.ajax)({
	            type: 'put',
	            url: '/api/pay/the_one_card/',
	            data: {
	                card_id: id
	            },
	            beforeSend: function beforeSend() {
	                $confirm.text('绑定中...').attr('disabled', true);
	            },
	            success: function success(data) {
	                if (data.status_code === 0) {
	                    $signItem.hide();
	                    return (0, _ui.ui_alert)('绑定成功', function () {
	                        var url = window.location.href;
	                        window.location.href = url;
	                    });
	                }
	            },
	            error: function error(xhr) {
	                $signItem.hide();
	                var result = JSON.parse(xhr.responseText);
	                return (0, _ui.ui_signError)(result.detail + '，一个账号只能绑定一张卡');
	            },
	            complete: function complete() {
	                $confirm.text('立即绑定').removeAttr('disabled');
	            }
	        });
	    };

	    $setBank.on('click', function () {
	        var bank_id = $(this).attr('data-id'),
	            bank_name = $(this).attr('data-name'),
	            bank_no = $(this).attr('data-no');

	        $signItem.find('.name').html(bank_name);
	        $signItem.find('.no').html(bank_no);
	        $confirm.attr('data-id', bank_id);
	        $signItem.show();
	    });

	    $confirm.on('click', function () {
	        var bank_id = $(this).attr('data-id');
	        put_bank(bank_id);
	    });

	    $('.bank-cancel').on('click', function () {
	        $signItem.hide();
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
	 *
	 * 引入fuel_alert.jade
	 * @param text 文字说明
	 * @param callback 回调函数
	 */

	var ui_alert = exports.ui_alert = function ui_alert(text, callback) {

	    var $alert = $('.fuel-alert'),
	        $button = $('.fuel-submit');

	    $alert.css('display', '-webkit-box').find('.fuel-text').text(text);

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
	var ui_confirm = exports.ui_confirm = function ui_confirm(title) {
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

	var ui_signError = exports.ui_signError = function ui_signError(sign) {
	    $('.error-sign').html(sign).removeClass('moveDown').addClass('moveDown').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
	        $(this).removeClass('moveDown');
	    });
	};
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },
/* 3 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
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
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);