webpackJsonp([0],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _createClass = (function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; })();

	__webpack_require__(2);

	var _functions = __webpack_require__(3);

	var _check = __webpack_require__(4);

	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

	(function () {

	    var $submit = $('button[type=submit]'),
	        $reduce = $('.reduce-num'),
	        $add = $('.add-num'),
	        $count = $('.value-num'),
	        balance = $('.fuel-balance').attr('data-balance') * 1,
	        $per = $('.fuel-per'),
	        per_value = $per.attr('data-per') * 1;

	    var MathCount = (function () {
	        function MathCount(count, amount) {
	            _classCallCheck(this, MathCount);

	            this.count = count;
	            this.amount = amount;
	            this.style = this.style.bind(this);
	        }

	        _createClass(MathCount, [{
	            key: 'add',
	            value: function add() {
	                this.count += 1;
	                this.style();
	            }
	        }, {
	            key: 'reduce',
	            value: function reduce() {
	                if (this.count <= 1) return;
	                this.count -= 1;
	                this.style();
	            }
	        }, {
	            key: 'style',
	            value: function style() {
	                $count.text(this.count);
	                $per.text(this.count * this.amount);
	                this.count <= 1 ? $reduce.addClass('num-disabled') : $reduce.removeClass('num-disabled');
	            }
	        }]);

	        return MathCount;
	    })();

	    var math = new MathCount(1, per_value);
	    $reduce.on('click', function () {
	        math.reduce();
	    });
	    $add.on('click', function () {
	        math.add();
	    });

	    $submit.on('click', function () {
	        if (balance > $per.text() * 1) return (0, _functions.signView)('余额不足！');
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