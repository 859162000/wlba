webpackJsonp([6],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj; };

	var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

	var _ui = __webpack_require__(2);

	var _from_validation = __webpack_require__(6);

	var _automatic_detection = __webpack_require__(5);

	var _api = __webpack_require__(3);

	var _simple_validation = __webpack_require__(8);

	var _bank_limit = __webpack_require__(9);

	(function () {

	    var $submit = $('button[type=submit]'),
	        $bank = $('select[name=bank]'),
	        $bankcard = $('input[name=bankcard]'),
	        $bankphone = $('input[name=bankphone]'),
	        $validation = $('input[name=validation]'),
	        $money = $('input[name=money]');

	    //---------------初始化操作start---------
	    var autolist = [{ target: $bank, required: true }, { target: $bankcard, required: true }, { target: $bankphone, required: true }, { target: $validation, required: true }, { target: $money, required: true }];
	    //自动检查
	    var auto = new _automatic_detection.Automatic({
	        submit: $submit,
	        checklist: autolist
	    });
	    auto.operationClear();

	    var codeAutoList = [{ target: $bank, required: true }, { target: $bankcard, required: true }, { target: $bankphone, required: true }];
	    var code = new _automatic_detection.Automatic({
	        submit: $('.regist-validation'),
	        checklist: codeAutoList
	    });
	    //---------------初始化操作end---------

	    //验证短信码所需表单
	    var checkOperation_validation = function checkOperation_validation() {
	        return new Promise(function (resolve, reject) {
	            function checkOperation() {
	                var checklist = [{ type: 'isEmpty', value: $bank.val() }, { type: 'bankCard', value: $bankcard.val() }, { type: 'phone', value: $bankphone.val() }];
	                return (0, _from_validation.check)(checklist);
	            }

	            var _checkOperation = checkOperation();

	            var _checkOperation2 = _slicedToArray(_checkOperation, 2);

	            var isThrough = _checkOperation2[0];
	            var sign = _checkOperation2[1];

	            if (isThrough) return resolve('验证成功');

	            (0, _ui.signModel)(sign);
	            return console.log('验证失败');
	        });
	    };

	    //验证表单
	    var checkOperation_submit = function checkOperation_submit() {
	        return new Promise(function (resolve, reject) {
	            function checkOperation() {
	                var checklist = [{ type: 'isEmpty', value: $bank.val() }, { type: 'bankCard', value: $bankcard.val() }, { type: 'phone', value: $bankphone.val() }, { type: 'isEmpty', value: $validation.val() }];
	                return (0, _from_validation.check)(checklist);
	            }

	            var _checkOperation3 = checkOperation();

	            var _checkOperation4 = _slicedToArray(_checkOperation3, 2);

	            var isThrough = _checkOperation4[0];
	            var sign = _checkOperation4[1];

	            if (isThrough) return resolve('验证成功');

	            (0, _ui.signModel)(sign);
	            return console.log('验证失败');
	        });
	    };

	    //渲染银行卡
	    var appendBanks = function appendBanks(banks) {
	        var str = '';
	        for (var bank in banks) {
	            str += '<option value ="' + banks[bank].gate_id + '" >' + banks[bank].name + '</option>';
	        }
	        return str;
	    };

	    //获取银行卡
	    var fetch_banklist = function fetch_banklist(callback) {
	        if (localStorage.getItem('bank')) {
	            var content = JSON.parse(localStorage.getItem('bank'));
	            $bank.append(appendBanks(content));
	            return callback && callback(content);
	        } else {
	            (0, _api.ajax)({
	                type: 'POST',
	                url: '/api/bank/list_new/',
	                success: function success(results) {
	                    if (results.ret_code === 0) {
	                        var _content = JSON.stringify(results.banks);
	                        $bank.append(appendBanks(results.banks));
	                        window.localStorage.setItem('bank', _content);
	                        return callback && callback(_content);
	                    } else {
	                        return alert(results.message);
	                    }
	                },
	                error: function error(data) {
	                    console.log(data);
	                }
	            });
	        }
	    };

	    fetch_banklist(function (banklist) {
	        _bank_limit.limit.getInstance({
	            target: $('.limit-bank-item'),
	            limit_data: banklist
	        });
	    });

	    var $validation_btn = $('button[name=validation_btn]');

	    var simple_validation = new _simple_validation.Simple_validation({
	        target: $validation_btn,
	        VALIDATION_URL: '/api/pay/deposit_new/'
	    });

	    //短信验证码
	    $validation_btn.on('click', function () {

	        simple_validation.set_check_list([{ type: 'isEmpty', value: $bank.val() }, { type: 'bankCard', value: $bankcard.val() }, { type: 'phone', value: $bankphone.val() }]);

	        simple_validation.set_ajax_data({
	            card_no: $bankcard.val(),
	            gate_id: $bank.val(),
	            phone: $bankphone.val(),
	            amount: 0.01
	        });
	        simple_validation.start();
	    });
	    //绑卡操作
	    $submit.on('click', function () {
	        var _this = this;

	        checkOperation_submit().then(function (result) {
	            var check_recharge = $(_this).attr('data-recharge');
	            if (check_recharge == 'true') {
	                confirm("充值金额为" + $money.val(), '确认充值', recharge, { firstRecharge: true });
	            } else {
	                recharge({ firstRecharge: false });
	            }
	        }).catch(function (result) {});
	    });

	    function recharge(check) {
	        org.ajax({
	            type: 'POST',
	            url: '/api/pay/cnp/dynnum_new/',
	            data: {
	                phone: $bankphone.val(),
	                vcode: $validation.val(),
	                order_id: $('input[name=order_id]').val(),
	                token: $('input[name=token]').val(),
	                set_the_one_card: true
	            },
	            beforeSend: function beforeSend() {
	                if (check.firstRecharge) {
	                    $submit.attr('disabled', 'disabled').text('充值中...');
	                } else {
	                    $submit.attr('disabled', 'disabled').text('绑卡中...');
	                }
	            },
	            success: function success(data) {
	                if (data.ret_code > 0) {
	                    return alert(data.message);
	                } else {
	                    if (check.firstRecharge) {
	                        $('.sign-main').css('display', '-webkit-box').find(".balance-sign").text(data.amount);
	                    } else {
	                        var _ret = function () {
	                            var next_url = (0, _api.getQueryStringByName)('next'),
	                                next = next_url == '' ? '/weixin/list/' : next_url;
	                            return {
	                                v: alert('绑卡成功！', function () {
	                                    window.location.href = next;
	                                })
	                            };
	                        }();

	                        if ((typeof _ret === 'undefined' ? 'undefined' : _typeof(_ret)) === "object") return _ret.v;
	                    }
	                }
	            },
	            error: function error(result) {
	                var data = JSON.parse(result.responseText);
	                return alert(data.detail);
	            },
	            complete: function complete() {
	                if (check.firstRecharge) {
	                    $submit.removeAttr('disabled').text('绑卡并充值');
	                } else {
	                    $submit.removeAttr('disabled').text('立即绑卡');
	                }
	            }
	        });
	    }
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

/***/ },
/* 3 */,
/* 4 */,
/* 5 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

	function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

	/**
	 * 表单自动检测
	 */

	var Automatic = exports.Automatic = function () {
	    function Automatic() {
	        var _ref = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];

	        var _ref$submit = _ref.submit;
	        var submit = _ref$submit === undefined ? null : _ref$submit;
	        var _ref$checklist = _ref.checklist;
	        var checklist = _ref$checklist === undefined ? [] : _ref$checklist;
	        var _ref$otherlist = _ref.otherlist;
	        var otherlist = _ref$otherlist === undefined ? [] : _ref$otherlist;
	        var _ref$done = _ref.done;
	        var done = _ref$done === undefined ? null : _ref$done;

	        _classCallCheck(this, Automatic);

	        var _ref2 = [submit, otherlist, checklist, done];
	        this.submit = _ref2[0];
	        this.otherlist = _ref2[1];
	        this.checklist = _ref2[2];
	        this.callback = _ref2[3];


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
	            var status = null;
	            this.checklist.forEach(function (dom) {
	                dom.target.on('input', function () {
	                    _self.style(dom.target);
	                    status = _self.canSubmit();
	                    _self.callback && _self.callback(status);
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
	                    if (dom.target.length == 0) {
	                        return true;
	                    }
	                    return false;
	                }
	            });

	            state ? this.submit.removeAttr('disabled') : this.submit.attr('disabled', 'true');
	            return state;
	        }
	    }, {
	        key: 'operationClear',
	        value: function operationClear() {
	            $('.wx-clear-input').on('click', function () {
	                $(this).siblings('input').val('').trigger('input');
	            });
	        }
	    }, {
	        key: 'operationPassword',
	        value: function operationPassword() {
	            $('.wx-password-operation').on('click', function () {
	                var type = $(this).siblings('input').attr('type');
	                if (type == 'text') {
	                    $(this).siblings().attr('type', 'password');
	                    $(this).addClass('wx-hide-password').removeClass('wx-show-password');
	                }
	                if (type == 'password') {
	                    $(this).siblings().attr('type', 'text');
	                    $(this).addClass('wx-show-password').removeClass('wx-hide-password');
	                }
	            });
	        }
	    }]);

	    return Automatic;
	}();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },
/* 6 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

	/**
	 * 表单验证
	 * @param checklist
	 * @returns {*[]}
	 */
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

/***/ },
/* 7 */,
/* 8 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	exports.Simple_validation = undefined;

	var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

	var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

	var _api = __webpack_require__(3);

	var _ui = __webpack_require__(2);

	var _from_validation = __webpack_require__(6);

	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

	/**
	 * 短信验证码按钮封装
	 * @param VALIDATION_URL 必填
	 * @param target  必填
	 * @param validation_form 必填
	 * @param callback 选填
	 */

	var Simple_validation = exports.Simple_validation = function () {
	    function Simple_validation() {
	        var _ref = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];

	        var _ref$target = _ref.target;
	        var target = _ref$target === undefined ? null : _ref$target;
	        var _ref$VALIDATION_URL = _ref.VALIDATION_URL;
	        var VALIDATION_URL = _ref$VALIDATION_URL === undefined ? null : _ref$VALIDATION_URL;
	        var _ref$callback = _ref.callback;
	        var callback = _ref$callback === undefined ? null : _ref$callback;

	        _classCallCheck(this, Simple_validation);

	        var _ref2 = [target, VALIDATION_URL, callback];
	        this.target = _ref2[0];
	        this.VALIDATION_URL = _ref2[1];
	        this.callback = _ref2[2];

	        this.post_data = null;
	        this.check_list = null;
	        this.intervalId = null;
	        this.before_validation = this.before_validation.bind(this);
	        this.timerFunction = this.timerFunction.bind(this);
	        this.execute_request = this.execute_request.bind(this);
	    }

	    _createClass(Simple_validation, [{
	        key: 'set_ajax_data',
	        value: function set_ajax_data(data_list) {
	            this.post_data = data_list;
	        }
	    }, {
	        key: 'set_check_list',
	        value: function set_check_list(list) {
	            this.check_list = list;
	        }
	    }, {
	        key: 'before_validation',
	        value: function before_validation() {
	            var checklist = this.check_list;

	            return new Promise(function (resolve, reject) {
	                function validation_operation() {
	                    var form_list = checklist;
	                    return (0, _from_validation.check)(form_list);
	                }

	                var _validation_operation = validation_operation();

	                var _validation_operation2 = _slicedToArray(_validation_operation, 2);

	                var isThrough = _validation_operation2[0];
	                var sign = _validation_operation2[1];

	                if (isThrough) return resolve('验证成功');

	                return reject(sign);
	            });
	        }
	    }, {
	        key: 'execute_request',
	        value: function execute_request() {
	            var $target = this.target,
	                VALIDATION_URL = this.VALIDATION_URL,
	                post_data = this.post_data,
	                intervalId = this.intervalId;

	            return new Promise(function (resolve, reject) {
	                (0, _api.ajax)({
	                    url: VALIDATION_URL,
	                    type: 'POST',
	                    data: post_data,
	                    beforeSend: function beforeSend() {
	                        $target.attr('disabled', 'disabled').text('发送中..');
	                    },
	                    success: function success(data) {
	                        if (data.ret_code > 0) {
	                            clearInterval(intervalId);
	                            $target.text('重新获取').removeAttr('disabled').css('background', '#50b143');

	                            return reject(data.message);
	                        } else {
	                            $("input[name='order_id']").val(data.order_id);
	                            $("input[name='token']").val(data.token);
	                            return resolve('短信已发送，请注意查收！');
	                        }
	                    },
	                    error: function error(result) {
	                        clearInterval(intervalId);
	                        $target.text('重新获取').removeAttr('disabled').css('background', '#50b143');
	                        return reject(result);
	                    }
	                });
	            });
	        }
	    }, {
	        key: 'timerFunction',
	        value: function timerFunction(count) {
	            var timerInside = function timerInside() {
	                if (count > 1) {
	                    count--;
	                    return this.target.text(count + '秒后可重发');
	                } else {
	                    clearInterval(this.intervalId);
	                    this.target.text('重新获取').removeAttr('disabled');
	                    return (0, _ui.signModel)('倒计时失效，请重新获取');
	                }
	            };
	            timerInside();
	            return this.intervalId = setInterval(timerInside, 1000);
	        }
	    }, {
	        key: 'start',
	        value: function start() {
	            var _this = this;

	            this.before_validation().then(function (result) {
	                console.log('验证通过');
	                return _this.execute_request();
	            }).then(function (result) {
	                (0, _ui.signModel)(result);
	                _this.timerFunction(60);
	            }).catch(function (result) {
	                return (0, _ui.signModel)(result);
	            });
	        }
	    }]);

	    return Simple_validation;
	}();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },
/* 9 */
/***/ function(module, exports) {

	"use strict";

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

	/**
	 * 银行限额
	 * @type {{getInstance}}
	 *
	 */

	var limit = exports.limit = function () {

	    var _instance = null;

	    var Limit = function () {
	        function Limit() {
	            var _ref = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];

	            var _ref$target = _ref.target;
	            var target = _ref$target === undefined ? null : _ref$target;
	            var _ref$limit_data = _ref.limit_data;
	            var limit_data = _ref$limit_data === undefined ? null : _ref$limit_data;

	            _classCallCheck(this, Limit);

	            var _ref2 = [target, limit_data];
	            this.target = _ref2[0];
	            this.limit_data = _ref2[1];


	            this._format_limit = this._format_limit.bind(this);
	            this.target.html(this._style(this.limit_data));
	        }

	        _createClass(Limit, [{
	            key: "_style",
	            value: function _style(limit_data) {
	                var string_list = '';
	                for (var i = 0; i < limit_data.length; i++) {
	                    string_list += "<div class='limit-bank-list'>";
	                    string_list += "<div class='limit-list-dec'>";
	                    string_list += "<div class='bank-name'>" + limit_data[i].name + "</div>";
	                    string_list += "<div class='bank-limit'>首次限额" + this._format_limit(limit_data[i].first_one) + "/单笔限额" + this._format_limit(limit_data[i].first_one) + "/日限额" + this._format_limit(limit_data[i].second_day) + "</div>";
	                    string_list += "</div>";
	                    string_list += "<div class='limit-list-icon " + limit_data[i].bank_id + "'></div>";
	                    string_list += "</div>";
	                }

	                return string_list;
	            }
	        }, {
	            key: "_format_limit",
	            value: function _format_limit(amount) {
	                var money = amount,
	                    reg = /^\d{5,}$/,
	                    reg2 = /^\d{4}$/;
	                if (reg.test(amount)) {
	                    return money = amount.replace('0000', '') + '万';
	                }
	                if (reg2.test(amount)) {
	                    return money = amount.replace('000', '') + '千';
	                }
	            }
	            //
	            //show(){
	            //    this.target.show()
	            //}
	            //
	            //hide(){
	            //    this.target.hide()
	            //}

	        }]);

	        return Limit;
	    }();

	    var getInstance = function getInstance(data) {
	        if (!_instance) {
	            _instance = new Limit(data);
	        }
	        return _instance;
	    };

	    return {
	        getInstance: getInstance
	    };
	}();

/***/ }
]);