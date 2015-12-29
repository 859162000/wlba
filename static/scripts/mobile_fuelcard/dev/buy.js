webpackJsonp([0],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = (function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; })();

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
	            this.count_amount = amount;
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
	            key: 'get_proerty',
	            value: function get_proerty() {
	                return [this.count, this.count_amount];
	            }
	        }, {
	            key: 'style',
	            value: function style() {
	                $count.text(this.count);
	                this.count_amount = this.count * this.amount;
	                $per.text(this.count * this.amount);
	                this.count <= 1 ? $reduce.addClass('num-disabled') : $reduce.removeClass('num-disabled');
	            }
	        }]);

	        return MathCount;
	    })();

	    var math = new MathCount(1, per_value);
	    var but_operation = function but_operation(data) {
	        (0, _functions.ajax)({
	            type: 'POST',
	            url: '/fuel_card/buy/',
	            data: data,
	            beforeSend: function beforeSend() {
	                $submit.attr('disabled', true).html('购买中...');
	            },
	            success: function success(result) {
	                return alert('成功购买加油卡' + result.data + '元', function () {
	                    var url = window.location.href;
	                    window.location.href = url;
	                });
	            },
	            error: function error(result) {
	                var data = JSON.parse(result.responseText);
	                return (0, _functions.signView)(data.message);
	            },
	            complete: function complete() {
	                $submit.removeAttr('disabled').html('确认购买并支付');
	            }
	        });
	    };

	    $reduce.on('click', function () {
	        math.reduce();
	    });
	    $add.on('click', function () {
	        math.add();
	    });

	    $submit.on('click', function () {
	        var p_id = $(this).attr('data-id');

	        var _math$get_proerty = math.get_proerty();

	        var _math$get_proerty2 = _slicedToArray(_math$get_proerty, 2);

	        var p_parts = _math$get_proerty2[0];
	        var amount = _math$get_proerty2[1];

	        if (balance < amount) return (0, _functions.signView)('余额不足！');

	        var push_data = {
	            'p_id': p_id,
	            'p_parts': p_parts,
	            'amount': amount
	        };
	        confirm("购买金额为" + amount, '确认购买', but_operation, push_data);
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

/***/ },
/* 3 */,
/* 4 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = (function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; })();

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	var check = exports.check = function check(checklist) {
	    var result = null;
	    var error = null;

	    $.each(checklist, function (index, target) {
	        var _validation$target$ty = validation[target.type](target.value);

	        var _validation$target$ty2 = _slicedToArray(_validation$target$ty, 2);

	        result = _validation$target$ty2[0];
	        error = _validation$target$ty2[1];

	        if (!result) return false;
	    });

	    return [result, error];
	};

	var validation = {
	    phone: function phone(str) {
	        var phone = parseInt($.trim(str)),
	            error = '请输入正确的手机号',
	            re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);

	        if (re.test(phone)) {
	            return [true, ''];
	        }
	        return [false, error];
	    },
	    password: function password(str) {
	        var error = '密码为6-20位数字/字母/符号/区分大小写',
	            re = new RegExp(/^\d{6,20}$/);
	        if (re.test($.trim(str))) {
	            return [true, ''];
	        }
	        return [false, error];
	    },
	    rePassword: function rePassword() {
	        var _ref = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];

	        var _ref$psw = _ref.psw;
	        var psw = _ref$psw === undefined ? null : _ref$psw;
	        var _ref$repeatPsw = _ref.repeatPsw;
	        var repeatPsw = _ref$repeatPsw === undefined ? null : _ref$repeatPsw;

	        var error = '两次密码不相同';
	        if (psw !== repeatPsw) {
	            return [false, error];
	        }
	        return [true, ''];
	    },
	    tranPassword: function tranPassword(str) {
	        var error = '交易密码为6位数字',
	            re = new RegExp(/^\d{6}$/);
	        if (re.test($.trim(str)) && !isNaN($.trim(str))) {
	            return [true, ''];
	        }
	        return [false, error];
	    },
	    bankCard: function bankCard(str) {
	        var error = '银行卡号不正确',
	            re = new RegExp(/^\d{12,20}$/);
	        if (re.test($.trim(str)) && !isNaN($.trim(str))) {
	            return [true, ''];
	        }
	        return [false, error];
	    },
	    idCard: function idCard(str) {
	        var error = '身份证号不正确',
	            re = new RegExp(/^.{15,18}$/);
	        if (re.test($.trim(str)) && !isNaN($.trim(str))) {
	            return [true, ''];
	        }
	        return [false, error];
	    },
	    money100: function money100(str) {
	        var error = '请输入100的倍数金额';
	        if (str % 100 === 0) {
	            return [true, ''];
	        }
	        return [false, error];
	    },
	    isEmpty: function isEmpty(str) {
	        var error = '请填写全部的表单';
	        if (str === '') {
	            return [false, error];
	        }
	        return [true, ''];
	    }
	};
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);