webpackJsonp([2],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = (function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; })();

	__webpack_require__(6);

	var _automatic_detection = __webpack_require__(5);

	var _functions = __webpack_require__(3);

	var _check = __webpack_require__(4);

	var _validation = __webpack_require__(7);

	(function () {

	    var $submit = $('button[type=submit]'),
	        $identifier = $('input[name=identifier]'),
	        $captcha_1 = $('input[name=captcha_1]'),
	        $captcha_0 = $('input[name=captcha_0]'),
	        $validate_code = $('input[name=validate_code]'),
	        $password = $('input[name=password]'),
	        $invite_code = $('input[name=invite_code]'),
	        $agreement = $('input[name=agreement]'),
	        $captcha = $('#captcha'),
	        autolist = [{ target: $identifier, required: true }, { target: $captcha_1, required: true }, { target: $validate_code, required: true }, { target: $password, required: true }, { target: $invite_code, required: false }];
	    //---------------初始化操作start---------

	    //自动检查
	    var auto = new _automatic_detection.Automatic({
	        submit: $submit,
	        checklist: autolist,
	        otherlist: [{ target: $agreement, required: true }]
	    });
	    auto.operation();
	    auto.operationPassword();
	    //---------------初始化操作end---------

	    //短信验证码
	    (0, _validation.validation)($identifier, $captcha_0, $captcha_1, $captcha);

	    //---------------注册操作start---------
	    //用户协议
	    $("#agreement").on('click', function () {
	        $(this).toggleClass('agreement');
	        $(this).hasClass('agreement') ? $agreement.attr('checked', 'checked') : $agreement.removeAttr('checked');
	        $identifier.trigger('input');
	    });

	    //验证表单
	    var checkOperation = function checkOperation() {
	        return new Promise(function (resolve, reject) {
	            function checkOperation() {
	                var checklist = [{ type: 'phone', value: $identifier.val() }, { type: 'isEmpty', value: $captcha_1.val() }, { type: 'isEmpty', value: $validate_code.val() }, { type: 'password', value: $password.val() }];
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

	    //注册
	    function regist(url) {
	        return new Promise(function (resolve, reject) {
	            (0, _functions.ajax)({
	                url: url,
	                type: 'POST',
	                data: {
	                    'identifier': $identifier.val(),
	                    'password': $password.val(),
	                    'captcha_0': $captcha_0.val(),
	                    'captcha_1': $captcha_1.val(),
	                    'validate_code': $validate_code.val(),
	                    'invite_code': 'weixin',
	                    'invite_phone': ''
	                },
	                beforeSend: function beforeSend() {
	                    $submit.text('注册中,请稍等...').attr('disabled', 'true');
	                },
	                success: function success(data) {
	                    resolve(data);
	                },
	                error: function error(xhr) {
	                    reject(xhr);
	                },
	                complete: function complete() {
	                    $submit.text('立即注册 ｜ 领取奖励').removeAttr('disabled');
	                }
	            });
	        });
	    }

	    $submit.on('click', function () {
	        checkOperation().then(function (result) {
	            console.log(result); //check success
	            return regist('/api/register/');
	        }).then(function (result) {
	            console.log('register success');
	            if (result.ret_code === 0) {
	                alert('success');
	                alert('实名认证成功', function () {
	                    window.location.href = '/fuel/regist/bank/';
	                });
	            }
	            if (result.ret_code > 0) {
	                (0, _functions.signView)(result.message);
	            }
	        }).catch(function (xhr) {
	            var result = JSON.parse(xhr.responseText);
	            if (xhr.status === 429) {
	                (0, _functions.signView)('系统繁忙，请稍候重试');
	            } else {
	                (0, _functions.signView)(result.message);
	            }
	        });
	    });
	    //---------------注册操作end---------
	})();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },
/* 1 */,
/* 2 */,
/* 3 */,
/* 4 */,
/* 5 */
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
/* 6 */
/***/ function(module, exports) {

	"use strict";

	Promise.prototype.done = function (onFulfilled, onRejected) {
	  this.then(onFulfilled, onRejected).catch(function (reason) {
	    // 抛出一个全局错误
	    setTimeout(function () {
	      throw reason;
	    }, 0);
	  });
	};

	Promise.prototype.finally = function (callback) {
	  var P = this.constructor;
	  return this.then(function (value) {
	    return P.resolve(callback()).then(function () {
	      return value;
	    });
	  }, function (reason) {
	    return P.resolve(callback()).then(function () {
	      throw reason;
	    });
	  });
	};

/***/ },
/* 7 */
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