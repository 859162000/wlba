webpackJsonp([5],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

	var _automatic_detection = __webpack_require__(5);

	var _api = __webpack_require__(3);

	var _ui = __webpack_require__(2);

	var _from_validation = __webpack_require__(6);

	(function () {

	    var $submit = $('button[type=submit]'),
	        $identifier = $('input[name=identifier]'),
	        $password = $('input[name=password]');

	    var autolist = [{ target: $identifier, required: true }, { target: $password, required: true }];
	    //自动检查
	    var auto = new _automatic_detection.Automatic({
	        submit: $submit,
	        checklist: autolist
	    });
	    auto.operationClear();
	    auto.operationPassword();

	    //---------------login操作start---------

	    //验证表单
	    var checkOperation = function checkOperation() {
	        return new Promise(function (resolve, reject) {
	            alert("check");
	            function checkOperation() {
	                var checklist = [{ type: 'phone', value: $identifier.val() }, { type: 'password', value: $password.val() }];
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
	    //登录
	    function login(url) {
	        return new Promise(function (resolve, reject) {
	            (0, _api.ajax)({
	                url: url,
	                type: 'POST',
	                data: {
	                    'identifier': $identifier.val(),
	                    'password': $password.val()
	                },
	                beforeSend: function beforeSend() {
	                    $submit.text('登录中,请稍等...').attr('disabled', 'true');
	                },
	                success: function success(data) {
	                    resolve(data);
	                },
	                error: function error(res) {
	                    reject(res);
	                },
	                complete: function complete() {
	                    $submit.text('登录网利宝').removeAttr('disabled');
	                }
	            });
	        });
	    }

	    $submit.on('click', function () {
	        alert(3);
	        checkOperation().then(function (result) {
	            console.log(result); //check success
	            return login('/weixin/api/login/');
	        }).then(function (result) {
	            console.log('login success');
	            var next_url = (0, _api.getQueryStringByName)('next');
	            window.location.href = next_url ? decodeURIComponent(decodeURIComponent(next_url)) : '/weixin/account/';
	        }).catch(function (res) {
	            if (res['status'] == 403) {
	                (0, _ui.signModel)('请勿重复提交');
	                return false;
	            }
	            var data = JSON.parse(res.responseText);
	            for (var key in data) {
	                data['__all__'] ? (0, _ui.signModel)(data['__all__'][0]) : (0, _ui.signModel)(data[key][0]);
	            }
	        });
	    });
	    //---------------login操作end---------
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
	            re = new RegExp(/^([0-9]{17}([0-9]|x|X){1})|([0-9]{15})$/);
	        if (re.test($.trim(str))) {
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
	    },
	    isMoney: function isMoney(str) {
	        var error = '请正确填写金额',
	            int = str * 1;
	        if (!isNaN(int) && int > 0) {
	            return [true, ''];
	        }
	        return [false, error];
	    }
	};
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);