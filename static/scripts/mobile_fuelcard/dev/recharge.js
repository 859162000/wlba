webpackJsonp([3],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _ui = __webpack_require__(2);

	var _automatic_detection = __webpack_require__(5);

	var _functions = __webpack_require__(3);

	(function () {
	    var $item = $('.fuel-recharge-warp'),
	        $bankName = $('.recharge-bank'),
	        $bankCard = $('.recharge-card'),
	        $amount = $('input[name=amount]'),
	        $submit = $('button[type=submit]');
	    var g_CARD = null,
	        g_GATE_ID = null,
	        g_AMOUNT = null;

	    //自动检查
	    var auto = new _automatic_detection.Automatic({
	        submit: $submit,
	        checklist: [{ target: $amount, required: true }]
	    });
	    auto.operation();

	    var on_card = function on_card() {
	        return new Promise(function (resolve, reject) {
	            (0, _functions.ajax)({
	                url: '/api/pay/the_one_card/',
	                type: 'GET',
	                success: function success(result) {
	                    $('.recharge-loding').hide();
	                    resolve(result);
	                },
	                error: function error(result) {
	                    reject(result);
	                }
	            });
	        });
	    };

	    var on_card_operation = function on_card_operation(data) {
	        var card = data.no.slice(0, 6) + '********' + data.no.slice(-4),
	            name = data.bank.name;
	        g_CARD = data.no.slice(0, 6) + data.no.slice(-4);
	        g_GATE_ID = data.bank.gate_id;

	        $item.show();
	        $bankCard.text(card);
	        $bankName.text(name);
	    };

	    var banl_list = function banl_list() {
	        (0, _functions.ajax)({
	            url: '/api/pay/cnp/list_new/',
	            type: 'POST',
	            success: function success(result) {
	                $('.recharge-loding').hide();
	                if (result.ret_code === 0) {
	                    result.cards.length === 0 ? $('.unbankcard').show() : $('.bankcard').show();
	                }

	                if (result.ret_code > 0 && result.ret_code != 20071) {
	                    return (0, _ui.ui_signError)(data.message);
	                }
	            },
	            error: function error(result) {
	                (0, _ui.ui_signError)('系统异常，请稍后再试');
	            }
	        });
	    };

	    var recharge = function recharge(data) {
	        (0, _functions.ajax)({
	            type: 'POST',
	            url: '/api/pay/deposit_new/',
	            data: data,
	            beforeSend: function beforeSend() {
	                $submit.attr('disabled', true).text("充值中..");
	            },
	            success: function success(results) {
	                if (results.ret_code > 0) {
	                    return (0, _ui.ui_signError)(results.message);
	                } else {
	                    return (0, _ui.ui_alert)('充值成功');
	                }
	            },
	            error: function error(results) {
	                if (results.status >= 403) {
	                    (0, _ui.ui_signError)('服务器繁忙，请稍后再试');
	                }
	            },
	            complete: function complete() {
	                $submit.removeAttr('disabled').text("立即充值");
	            }
	        });
	    };

	    /**
	     * 判断有无同卡进出卡，有的话充值，没有做相应处理
	     */
	    on_card().then(function (result) {
	        //有同卡
	        on_card_operation(result);
	    }).catch(function () {
	        //无同卡
	        return banl_list();
	    });

	    $submit.on('click', function () {
	        var AMOUNT = $amount.val() * 1;

	        if (AMOUNT == 0 || !AMOUNT) {
	            return (0, _ui.ui_signError)('请输入充值金额');
	        }
	        var push_data = {
	            phone: '',
	            card_no: g_CARD,
	            amount: AMOUNT,
	            gate_id: g_GATE_ID
	        };
	        (0, _ui.ui_confirm)("充值金额为" + AMOUNT, '确认充值', recharge, push_data);
	    });
	})();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },

/***/ 5:
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _createClass = (function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; })();

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

	var Automatic = exports.Automatic = (function () {
	    function Automatic() {
	        var _ref = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];

	        var _ref$submit = _ref.submit;
	        var submit = _ref$submit === undefined ? null : _ref$submit;
	        var _ref$checklist = _ref.checklist;
	        var checklist = _ref$checklist === undefined ? [] : _ref$checklist;
	        var _ref$otherlist = _ref.otherlist;
	        var otherlist = _ref$otherlist === undefined ? [] : _ref$otherlist;

	        _classCallCheck(this, Automatic);

	        var _ref2 = [submit, otherlist, checklist];
	        this.submit = _ref2[0];
	        this.otherlist = _ref2[1];
	        this.checklist = _ref2[2];

	        this.allCheck = this.allRequire();
	        this.canSubmit = this.canSubmit.bind(this);
	        this.isEmptyString = this.isEmptyString.bind(this);
	        this.isEmptyArray = this.isEmptyArray.bind(this);
	        this.check();
	    }

	    _createClass(Automatic, [{
	        key: 'allRequire',
	        value: function allRequire() {
	            var allCheck = [].concat(_toConsumableArray(this.checklist), _toConsumableArray(this.otherlist));
	            return allCheck.filter(function (target) {
	                if (target.required) return true;
	                return false;
	            });
	        }
	    }, {
	        key: 'isEmptyArray',
	        value: function isEmptyArray(array) {
	            if (array.length === 0) return true;
	            return false;
	        }
	    }, {
	        key: 'isEmptyString',
	        value: function isEmptyString(str) {
	            if (str == '') return true;
	            return false;
	        }
	    }, {
	        key: 'check',
	        value: function check() {
	            if (this.isEmptyArray(this.checklist)) return console.log('checklist is none');

	            var _self = this;
	            this.checklist.forEach(function (dom) {
	                dom.target.on('input', function () {
	                    _self.style(dom.target);
	                    _self.canSubmit();
	                });
	            });
	        }
	    }, {
	        key: 'style',
	        value: function style(target) {

	            var isEmpty = this.isEmptyString(target.val()),
	                icon = target.attr('data-icon'),
	                othericon = target.attr('data-other'),
	                operation = target.attr('data-operation');

	            //等于空
	            if (isEmpty) {
	                if (icon != '') target.siblings('.' + icon).removeClass('active');
	                if (othericon != '') $('.' + othericon).attr('disabled', 'true');
	                if (operation != '') target.siblings('.' + operation).hide();
	            }

	            //不等于空
	            if (!isEmpty) {
	                if (icon != '') target.siblings('.' + icon).addClass('active');
	                if (othericon != '') $('.' + othericon).removeAttr('disabled');
	                if (operation != '') target.siblings('.' + operation).show();
	            }
	        }
	    }, {
	        key: 'canSubmit',
	        value: function canSubmit() {
	            var type = 'text|tel|password|select|';
	            var _self = this;

	            var state = this.allCheck.every(function (dom) {
	                var target = dom.target;

	                if (type.indexOf(target.attr('type')) >= 0) {
	                    if (_self.isEmptyString(target.val())) {
	                        return false;
	                    }
	                    return true;
	                }

	                if (type.indexOf(dom.target) < 0) {
	                    if (target.attr('type') == 'checkbox' && target.prop('checked')) {
	                        return true;
	                    }
	                    return false;
	                }
	            });

	            state ? this.submit.removeAttr('disabled') : this.submit.attr('disabled', 'true');
	        }
	    }, {
	        key: 'operation',
	        value: function operation() {
	            $('.fuel-clear-input').on('click', function () {
	                $(this).siblings('input').val('').trigger('input');
	            });
	        }
	    }, {
	        key: 'operationPassword',
	        value: function operationPassword() {
	            $('.fuel-password-operation').on('click', function () {
	                var type = $(this).siblings('input').attr('type');
	                if (type == 'text') {
	                    $(this).siblings().attr('type', 'password');
	                    $(this).addClass('fuel-hide-password').removeClass('fuel-show-password');
	                }
	                if (type == 'password') {
	                    $(this).siblings().attr('type', 'text');
	                    $(this).addClass('fuel-show-password').removeClass('fuel-hide-password');
	                }
	            });
	        }
	    }]);

	    return Automatic;
	})();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }

});