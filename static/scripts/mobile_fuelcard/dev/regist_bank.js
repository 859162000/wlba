webpackJsonp([4],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = (function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; })();

	var _automatic_detection = __webpack_require__(2);

	var _functions = __webpack_require__(3);

	var _check = __webpack_require__(4);

	var _validation = __webpack_require__(6);

	(function () {

	    var $submit = $('button[type=submit]'),
	        $bank = $('select[name=bank]'),
	        $bankcard = $('input[name=bankcard]'),
	        $bankphone = $('input[name=bankphone]'),
	        $validation = $('input[name=validation]'),
	        $validate_operation = $('button[name=validate_operation]'),
	        autolist = [{ target: $bank, required: true }, { target: $bankcard, required: true }, { target: $bankphone, required: true }, { target: $validation, required: true }];
	    //---------------初始化操作start---------
	    //获取银行卡列表
	    ~(function () {
	        if (localStorage.getItem('bank')) {
	            var content = JSON.parse(localStorage.getItem('bank'));
	            return $bank.append(appendBanks(content));
	        }
	        (0, _functions.ajax)({
	            type: 'POST',
	            url: '/api/bank/list_new/',
	            success: function success(results) {
	                if (results.ret_code === 0) {
	                    var content = JSON.stringify(results.banks);

	                    $bank.append(appendBanks(results.banks));
	                    window.localStorage.setItem('bank', content);
	                } else {
	                    return (0, _functions.signView)(results.message);
	                }
	            },
	            error: function error(data) {
	                console.log(data);
	            }
	        });
	        function appendBanks(banks) {
	            var str = '';
	            for (var bank in banks) {
	                str += '<option value = \'' + banks[bank].gate_id + '\' >' + banks[bank].name + '</option>';
	            }
	            return str;
	        }
	    })();

	    //自动检查
	    var auto = new _automatic_detection.Automatic({
	        submit: $submit,
	        checklist: autolist
	    });
	    auto.operation();

	    $('select[name=bank]').change(function () {
	        var icon = $(this).attr('data-icon');
	        if ($(this).val() == '') {
	            $(this).siblings('.' + icon).removeClass('active');
	        } else {
	            $(this).siblings('.' + icon).addClass('active');
	        }
	        $('input[name=password]').trigger('input');
	    });

	    //---------------初始化操作end---------

	    //短信验证码
	    //验证表单
	    var checkOperation_bank = function checkOperation_bank() {
	        return new Promise(function (resolve, reject) {
	            function checkOperation() {
	                var checklist = [{ type: 'isEmpty', value: $bank.val() }, { type: 'bankCard', value: $bankcard.val() }, { type: 'phone', value: $bankphone.val() }];
	                return (0, _check.check)(checklist);
	            }

	            var _checkOperation = checkOperation();

	            var _checkOperation2 = _slicedToArray(_checkOperation, 2);

	            var isThrough = _checkOperation2[0];
	            var sign = _checkOperation2[1];

	            if (isThrough) return resolve('验证成功');

	            (0, _functions.signView)(sign);
	            return console.log('验证失败');
	        });
	    };

	    var get_validation = function get_validation(url) {
	        return new Promise(function (resolve, reject) {
	            (0, _functions.ajax)({
	                url: url,
	                type: 'POST',
	                data: {
	                    'card_no': $bankcard.val(),
	                    'amount': 0.01,
	                    'phone': $bankphone.val(),
	                    'gate_id': $bank.val()
	                },
	                beforeSend: function beforeSend() {
	                    $validate_operation.attr('disabled', 'disabled').text('发送中..');
	                },
	                success: function success(results) {
	                    if (results.ret_code === 0) {
	                        (0, _functions.signView)(results.message);
	                        $("input[name='order_id']").val(results.order_id);
	                        $("input[name='token']").val(results.token);
	                        return resolve('短信已发送，请注意查收！');
	                    }

	                    if (results.ret_code > 0) {
	                        (0, _functions.signView)(results.message);
	                        return reject('获取短信验证码错误');
	                    }
	                },
	                error: function error(xhr) {
	                    reject(xhr);
	                },
	                complete: function complete() {
	                    $validate_operation.removeAttr('disabled').text('获取验证码');
	                }
	            });
	        });
	    };

	    //倒计时
	    var timerFunction = function timerFunction(count) {
	        return new Promise(function (resolve, reject) {
	            var timerFunction = function timerFunction() {
	                if (count > 1) {
	                    count--;
	                    return $validate_operation.text(count + '秒后可重发');
	                } else {
	                    clearInterval(intervalId);
	                    $validate_operation.text('重新获取').removeAttr('disabled');
	                    (0, _functions.signView)('倒计时失效，请重新获取');
	                    return reject('倒计时失效，请重新获取');
	                }
	            };
	            timerFunction();
	            return intervalId = setInterval(timerFunction, 1000);
	        });
	    };

	    $validate_operation.on('click', function () {
	        checkOperation_bank().then(function (result) {
	            console.log(result);
	            return get_validation('/api/pay/deposit_new/');
	        }).then(function (result) {
	            console.log('短信发送成功，自信倒计时');
	            var count = 60;
	            return timerFunction(count);
	        }).catch(function (message) {
	            console.log(message);
	        });
	    });

	    //---------------绑卡操作start---------

	    //验证表单
	    var checkOperation = function checkOperation() {
	        return new Promise(function (resolve, reject) {
	            function checkOperation() {
	                var checklist = [{ type: 'isEmpty', value: $bank.val() }, { type: 'bankCard', value: $bankcard.val() }, { type: 'phone', value: $bankphone.val() }, { type: 'isEmpty', value: $validation.val() }];
	                return (0, _check.check)(checklist);
	            }

	            var _checkOperation3 = checkOperation();

	            var _checkOperation4 = _slicedToArray(_checkOperation3, 2);

	            var isThrough = _checkOperation4[0];
	            var sign = _checkOperation4[1];

	            if (isThrough) return resolve('验证成功');

	            (0, _functions.signView)(sign);
	            return console.log('验证失败');
	        });
	    };

	    //绑卡
	    function set_bank(url) {
	        return new Promise(function (resolve, reject) {
	            (0, _functions.ajax)({
	                url: url,
	                type: 'POST',
	                data: {
	                    phone: $bankphone.val(),
	                    vcode: $validation.val(),
	                    order_id: $('input[name=order_id]').val(),
	                    token: $('input[name=token]').val(),
	                    set_the_one_card: true
	                },
	                beforeSend: function beforeSend() {
	                    $submit.text('绑定中,请稍等...').attr('disabled', 'true');
	                },
	                success: function success(data) {
	                    if (data.ret_code > 0) {
	                        reject(data.message);
	                        return (0, _functions.signView)(data.message);
	                    } else {
	                        return alert('恭喜你，绑卡成功！', function () {
	                            resolve(data.message);
	                            window.location.href = '/fuel/regist/end/';
	                        });
	                    }
	                },
	                error: function error(xhr) {
	                    reject(xhr);
	                },
	                complete: function complete() {
	                    $submit.text('绑定银行卡').removeAttr('disabled');
	                }
	            });
	        });
	    }

	    $submit.on('click', function () {
	        checkOperation().then(function (result) {
	            console.log(result); //check success
	            return set_bank('/api/pay/cnp/dynnum_new/');
	        }).then(function (result) {
	            console.log(result);
	        }).catch(function (xhr) {
	            console.log(result);
	        });
	    });
	    //---------------绑卡操作end---------
	})();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },
/* 1 */,
/* 2 */
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

/***/ },
/* 3 */,
/* 4 */,
/* 5 */,
/* 6 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = (function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; })();

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	exports.validation = undefined;

	var _functions = __webpack_require__(3);

	var _check = __webpack_require__(4);

	var validation = exports.validation = function validation($phone, $captcha_0, $captcha_1, $captcha) {

	    var intervalId = null;
	    var $validate_operation = $('button[name=validate_operation]');

	    //获取图像验证码
	    function validation() {
	        var url = '/captcha/refresh/?v=' + new Date().getTime();
	        $.get(url, function (result) {
	            $captcha.attr('src', result['image_url']);
	            $captcha_0.val(result['key']);
	        });
	    }

	    validation();

	    //验证表单
	    var checkOperation = function checkOperation(phone) {
	        return new Promise(function (resolve, reject) {
	            function checkOperation() {
	                var checklist = [{ type: 'phone', value: phone }];
	                return (0, _check.check)(checklist);
	            }

	            var _checkOperation = checkOperation();

	            var _checkOperation2 = _slicedToArray(_checkOperation, 2);

	            var isThrough = _checkOperation2[0];
	            var sign = _checkOperation2[1];

	            if (isThrough) return resolve('验证成功');

	            return reject(sign);
	        });
	    };

	    //获取短信验证码
	    function fetchValidation(phone, captcha_0, captcha_1) {
	        return new Promise(function (resolve, reject) {
	            (0, _functions.ajax)({
	                url: '/api/phone_validation_code/' + phone + '/',
	                data: {
	                    captcha_0: captcha_0,
	                    captcha_1: captcha_1
	                },
	                type: 'POST',
	                beforeSend: function beforeSend() {
	                    $validate_operation.attr('disabled', 'disabled').text('发送中..');
	                },
	                success: function success() {
	                    resolve('短信已发送，请注意查收！');
	                },

	                error: function error(xhr) {
	                    var result = JSON.parse(xhr.responseText);
	                    $validate_operation.removeAttr('disabled').text('获取验证码');
	                    clearInterval(intervalId);
	                    validation();
	                    return reject(result.message);
	                }
	            });
	        });
	    }

	    //倒计时
	    function timerFunction(count) {
	        return new Promise(function (resolve, reject) {
	            var timerFunction = function timerFunction() {
	                if (count > 1) {
	                    count--;
	                    return $validate_operation.text(count + '秒后可重发');
	                } else {
	                    clearInterval(intervalId);
	                    $validate_operation.text('重新获取').removeAttr('disabled');
	                    validation();
	                    return reject('倒计时失效，请重新获取');
	                }
	            };
	            timerFunction();
	            return intervalId = setInterval(timerFunction, 1000);
	        });
	    }

	    //图像验证码
	    $captcha.on('click', function () {
	        validation();
	    });

	    //短信验证码
	    $validate_operation.on('click', function () {
	        var phone = $phone.val(),
	            captcha_0 = $captcha_0.val(),
	            captcha_1 = $captcha_1.val();

	        chained(phone, captcha_0, captcha_1);
	    });

	    function chained(phone, captcha_0, captcha_1) {
	        /**
	         * 所有的逻辑在这里，获取短信验证码的时候，先检查手机号是否符合，
	         * 成功后 fetchValidation（发送短信请求）
	         * 成功后 timerFunction（倒计时）
	         */
	        checkOperation(phone).then(function () {
	            console.log('验证成功');
	            return fetchValidation(phone, captcha_0, captcha_1);
	        }).then(function (message) {
	            (0, _functions.signView)(message);
	            console.log('短信发送成功');
	            var count = 60;
	            return timerFunction(count);
	        }).catch(function (message) {
	            (0, _functions.signView)(message);
	        });
	    }
	};
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);