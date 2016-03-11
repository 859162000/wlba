webpackJsonp([12],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

	var _automatic_detection = __webpack_require__(5);

	var _api = __webpack_require__(3);

	var _ui = __webpack_require__(2);

	var _from_validation = __webpack_require__(6);

	var _images_validation = __webpack_require__(12);

	(function () {

	    var $submit = $('button[type=submit]'),
	        $identifier = $('input[name=identifier]'),
	        $captcha_1 = $('input[name=captcha_1]'),
	        $captcha_0 = $('input[name=captcha_0]'),
	        $validate_code = $('input[name=validate_code]'),
	        $password = $('input[name=password]'),
	        $invite_code = $('input[name=invite_code]'),
	        $agreement = $('input[name=agreement]'),
	        $captcha = $('#captcha');

	    //---------------初始化操作start---------
	    var autolist = [{ target: $identifier, required: true }, { target: $captcha_1, required: true }, { target: $validate_code, required: true }, { target: $password, required: true }, { target: $invite_code, required: false }];
	    //自动检查
	    var auto = new _automatic_detection.Automatic({
	        submit: $submit,
	        checklist: autolist,
	        otherlist: [{ target: $agreement, required: true }]
	    });
	    auto.operationClear();
	    auto.operationPassword();
	    //---------------初始化操作end---------

	    //短信验证码
	    (0, _images_validation.validation)($identifier, $captcha_0, $captcha_1, $captcha);

	    //---------------注册操作start---------
	    //用户协议
	    $("#agreement").on('click', function () {
	        $(this).toggleClass('agreement');
	        $(this).hasClass('agreement') ? $agreement.attr('checked', 'checked') : $agreement.removeAttr('checked');
	        $identifier.trigger('input');
	    });
	    //显示协议
	    var $showXiyi = $('.xieyi-btn'),
	        $cancelXiyi = $('.cancel-xiyie'),
	        $protocolDiv = $('.regist-protocol-div');
	    $showXiyi.on('click', function (event) {
	        event.preventDefault();
	        $protocolDiv.css('display', 'block');
	        setTimeout(function () {
	            $protocolDiv.css('top', '0%');
	        }, 0);
	    });
	    //关闭协议
	    $cancelXiyi.on('click', function () {
	        $protocolDiv.css('top', '100%');
	        setTimeout(function () {
	            $protocolDiv.css('display', 'none');
	        }, 200);
	    });

	    //验证表单
	    var checkOperation = function checkOperation() {
	        return new Promise(function (resolve, reject) {
	            function checkOperation() {
	                var checklist = [{ type: 'phone', value: $identifier.val() }, { type: 'isEmpty', value: $captcha_1.val() }, { type: 'isEmpty', value: $validate_code.val() }, { type: 'password', value: $password.val() }];
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

	    //注册
	    function register(url) {
	        return new Promise(function (resolve, reject) {
	            (0, _api.ajax)({
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
	            return register('/api/register/');
	        }).then(function (result) {
	            console.log('register success');
	            if (result.ret_code === 0) {
	                alert('注册成功', function () {
	                    var next = (0, _api.getQueryStringByName)('next') == '' ? '/weixin/regist/first/' : (0, _api.getQueryStringByName)('next');
	                    next = (0, _api.getQueryStringByName)('mobile') == '' ? next : next + '&mobile=' + (0, _api.getQueryStringByName)('mobile');
	                    next = (0, _api.getQueryStringByName)('serverId') == '' ? next : next + '&serverId=' + (0, _api.getQueryStringByName)('serverId');
	                    window.location.href = next;
	                });
	            }
	            if (result.ret_code > 0) {
	                (0, _ui.signModel)(result.message);
	            }
	        }).catch(function (xhr) {
	            var result = JSON.parse(xhr.responseText);
	            if (xhr.status === 429) {
	                (0, _ui.signModel)('系统繁忙，请稍候重试');
	            } else {
	                (0, _ui.signModel)(result.message);
	            }
	        });
	    });
	    //---------------注册操作end---------
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
/* 8 */,
/* 9 */,
/* 10 */,
/* 11 */,
/* 12 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	exports.validation = undefined;

	var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

	var _api = __webpack_require__(3);

	var _ui = __webpack_require__(2);

	var _from_validation = __webpack_require__(6);

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
	                return (0, _from_validation.check)(checklist);
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
	            (0, _api.ajax)({
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
	            (0, _ui.signModel)(message);
	            console.log('短信发送成功');
	            var count = 60;
	            return timerFunction(count);
	        }).catch(function (message) {
	            (0, _ui.signModel)(message);
	        });
	    }
	};
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);