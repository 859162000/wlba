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

/***/ }
]);