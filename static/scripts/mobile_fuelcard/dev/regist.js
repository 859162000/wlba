webpackJsonp([1],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = (function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; })();

	__webpack_require__(4);

	var _automatic_detection = __webpack_require__(2);

	var _functions = __webpack_require__(3);

	var _check = __webpack_require__(5);

	var _validation = __webpack_require__(6);

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
	    //----------短信验证码start
	    (0, _validation.validation)($identifier, $captcha_0, $captcha_1, $captcha);

	    //----------短信验证码end
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
	            return reject('验证失败');
	        });
	    };
	    //短信验证码

	    //注册
	    function regist(url) {
	        return new Promise(function (resolve, reject) {
	            console.log('iam');
	            (0, _functions.ajax)({
	                url: url,
	                type: 'POST',
	                data: {
	                    'identifier': $identifier.val(),
	                    'password': $password.val(),
	                    'captcha_0': $captcha_0.val(),
	                    'captcha_1': $captcha_1.val(),
	                    'validate_code': $validation.val(),
	                    'invite_code': 'weixin',
	                    'invite_phone': ''
	                },
	                beforeSend: function beforeSend() {
	                    $submit.text('注册中,请稍等...');
	                },
	                success: function success(data) {
	                    resolve(data);
	                },
	                error: function error(xhr) {
	                    reject(xhr);
	                },
	                complete: function complete() {
	                    $submit.text('立即注册 ｜ 领取奖励');
	                }
	            });
	        });
	    }

	    $submit.on('click', function () {
	        checkOperation().then(function (result) {
	            console.log(result); //check success
	            return regist('/api/register/');
	        }).catch(function (error) {
	            console.log(error); //check error
	        }).then(function (result) {
	            console.log('register success');
	            if (result.ret_code === 0) {
	                alert('success');
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
	var signView = exports.signView = function signView(sign) {
	    $('.error-sign').html(sign).removeClass('moveDown').addClass('moveDown').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
	        $(this).removeClass('moveDown');
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

/***/ },
/* 4 */
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
/* 5 */
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
	    idCard: function idCard(str) {
	        var error = '银行卡号不正确',
	            re = new RegExp(/^\d{12,20}$/);
	        if (re.test($.trim(str)) && !isNaN($.trim(str))) {
	            return [true, ''];
	        }
	        return [false, error];
	    },
	    bankCard: function bankCard(str) {
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
/* 6 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = (function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; })();

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	exports.validation = undefined;

	var _functions = __webpack_require__(3);

	var _check = __webpack_require__(5);

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

	            (0, _functions.signView)(sign);
	            return reject('验证失败');
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
	                    $('button[name=validate_operation]').attr('disabled', 'disabled');
	                },
	                success: function success() {
	                    resolve('短信已发送，请注意查收！');
	                },

	                error: function error(xhr) {
	                    clearInterval(intervalId);
	                    var result = JSON.parse(xhr.responseText);
	                    reject(result.message);
	                }
	            });
	        });
	    }
	    //倒计时
	    function timerFunction() {
	        return new Promise(function (resolve, reject) {
	            var timerFunction = function timerFunction() {
	                if (count >= 1) {
	                    count--;
	                    return $('button[name=validate_operation]').text(count + '秒后可重发');
	                } else {
	                    return reject('时间到了');
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
	            return fetchValidation(phone, captcha_0, captcha_1);
	        }).then(function (message) {
	            (0, _functions.signView)(message);
	            return timerFunction();
	        }).catch(function (message) {
	            (0, _functions.signView)(message);
	        }).catch(function (message) {
	            clearInterval(intervalId);
	            $('button[name=validate_operation]').text('重新获取').removeAttr('disabled');
	            validation();
	        });
	    }
	};
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);