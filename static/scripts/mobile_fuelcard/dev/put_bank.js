webpackJsonp([2],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	__webpack_require__(2);

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
	                    return alert('绑定成功', function () {
	                        var url = window.location.href;
	                        window.location.href = url;
	                    });
	                }
	            },
	            error: function error(xhr) {
	                $signItem.hide();
	                var result = JSON.parse(xhr.responseText);
	                return (0, _functions.signView)(result.detail + '，一个账号只能绑定一张卡');
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

	/**
	 *
	 * 引入fuel_alert.jade
	 * @param text 文字说明
	 * @param callback 回调函数
	 */
	window.alert = function (text, callback) {

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
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);