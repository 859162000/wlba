webpackJsonp([11],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

	var _automatic_detection = __webpack_require__(5);

	var _api = __webpack_require__(3);

	var _ui = __webpack_require__(2);

	var _from_validation = __webpack_require__(6);

	var _trade_validation = __webpack_require__(7);

	(function () {

	    var $submit = $('button[type=submit]'),
	        $amount = $('input[name=amount]'),
	        $card_no = $("input[name='card_no']"),
	        $loading = $(".recharge-loding"),
	        $recharge_body = $('.recharge-main'),
	        $bank_name = $(".bank-txt-name");

	    var tradeStatus = null;

	    //自动检查
	    var autolist = [{ target: $amount, required: true }];

	    var auto = new _automatic_detection.Automatic({
	        submit: $submit,
	        checklist: autolist
	    });
	    auto.operationClear();

	    //验证表单
	    var checkOperation = function checkOperation() {
	        return new Promise(function (resolve, reject) {
	            function checkOperation() {
	                var checklist = [{ type: 'isEmpty', value: $amount.val() }];
	                return (0, _from_validation.check)(checklist);
	            }

	            var _checkOperation = checkOperation();

	            var _checkOperation2 = _slicedToArray(_checkOperation, 2);

	            var isThrough = _checkOperation2[0];
	            var sign = _checkOperation2[1];

	            if (isThrough) return resolve({ message: '验证成功', amount: $amount.val() });

	            (0, _ui.signModel)(sign);
	            return console.log('验证失败');
	        });
	    };

	    //confirm
	    var confirm_ui = function confirm_ui(amount) {
	        return new Promise(function (resolve, reject) {
	            confirm('充值金额为' + amount, '确认充值', function () {
	                resolve(amount);
	            });
	        });
	    };
	    var seachTrade = function seachTrade() {
	        (0, _api.ajax)({
	            url: '/api/profile/',
	            type: 'GET',
	            success: function success(result) {
	                tradeStatus = result.trade_pwd_is_set ? true : false;
	            }
	        });
	    };

	    //设置交易密码
	    var trade_set = function trade_set(model_operation, new_trade_pwd) {
	        (0, _api.ajax)({
	            url: '/api/trade_pwd/',
	            type: 'post',
	            data: {
	                action_type: 1,
	                new_trade_pwd: new_trade_pwd
	            },
	            success: function success(result) {
	                model_operation.loadingHide();
	                model_operation.destroy();
	                model_operation.layoutHide();
	                if (result.ret_code == 0) {
	                    _trade_validation.Deal_ui.show_alert('success', function () {
	                        window.location = window.location.href;
	                    }, '交易密码设置成功，请牢记！');
	                }

	                if (result.ret_code > 0) {
	                    alert(result.message);
	                }
	            }
	        });
	    };
	    //交易密码
	    var trade_operation = function trade_operation(amount) {
	        tradeStatus ? entry_trade() : set_trade();

	        function entry_trade() {
	            var operation = new _trade_validation.Trade({
	                header: '请输入交易密码',
	                explain: '充值金额<br>￥' + amount,
	                done: function done(result) {
	                    operation.loadingShow();

	                    recharge(operation, result.password);
	                }
	            });
	            operation.layoutShow();
	        }

	        var set_trade_data = {};
	        function set_trade() {
	            var set_operation_1 = new _trade_validation.Trade({
	                header: '设置交易密码',
	                explain: '请设置6位数字作为交易密码',
	                done: function done(result) {
	                    set_trade_data.password_1 = result.password;
	                    set_operation_1.destroy();
	                    set_operation_1.layoutHide();
	                    set_operation_2();
	                }
	            });
	            set_operation_1.layoutShow();

	            function set_operation_2() {
	                var set_operation_2 = new _trade_validation.Trade({
	                    header: '设置交易密码',
	                    explain: '请再次确认交易密码',
	                    done: function done(result) {
	                        set_trade_data.password_2 = result.password;
	                        if (set_trade_data.password_2 != set_trade_data.password_1) {
	                            set_operation_2.destroy();
	                            set_operation_2.layoutHide();
	                            return _trade_validation.Deal_ui.show_alert('error', function () {
	                                set_trade();
	                            });
	                        }
	                        set_operation_2.loadingShow();

	                        //设置交易密码
	                        trade_set(set_operation_2, result.password);
	                    }
	                });
	                set_operation_2.layoutShow();
	            }
	        }
	    };

	    //渲染同卡进出的卡的卡片
	    var dataCopy = null;
	    var renderCard = function renderCard(data) {
	        var card = data.no.slice(0, 6) + '********' + data.no.slice(-4);
	        $loading.hide();
	        $recharge_body.show();
	        dataCopy = data;
	        $amount.attr('placeholder', '该银行单笔限额' + data.bank.bank_limit.second_one / 10000 + '万元');
	        $card_no.val(card);
	        $bank_name.text(data.bank.name);
	    };

	    //获取银行卡列表
	    var fetchBanks = function fetchBanks() {
	        (0, _api.ajax)({
	            url: '/api/pay/cnp/list_new/',
	            type: 'POST',
	            success: function success(data) {
	                if (data.ret_code === 0) {
	                    $loading.hide();
	                    data.cards.length === 0 ? $('.unbankcard').show() : $('.bankcard').show();
	                }
	                if (data.ret_code > 0 && data.ret_code != 20071) {
	                    return alert(data.message);
	                }
	            },
	            error: function error(data) {
	                return alert('系统异常，请稍后再试');
	            }
	        });
	    };

	    //判断是否有同卡绑定
	    var the_one_card = function the_one_card() {
	        (0, _api.ajax)({
	            url: '/api/pay/the_one_card/',
	            type: 'get',
	            success: function success(data) {
	                //同卡进出
	                renderCard(data);
	                //判断是否设置交易密码
	                seachTrade();
	            },
	            error: function error(data) {
	                //没有同卡进出
	                if (data.status === 403) {
	                    fetchBanks();
	                }
	            }
	        });
	    };
	    //充值接口
	    var recharge = function recharge(trade_operation, trade_pwd) {
	        var card = dataCopy.no.slice(0, 6) + dataCopy.no.slice(-4),
	            gate_id = dataCopy.bank.gate_id,
	            amount = $amount.val() * 1;

	        (0, _api.ajax)({
	            type: 'POST',
	            url: '/api/pay/deposit_new/',
	            data: {
	                phone: '',
	                card_no: card,
	                amount: amount,
	                gate_id: gate_id,
	                trade_pwd: trade_pwd
	            },
	            beforeSend: function beforeSend() {
	                $submit.attr('disabled', true).text("充值中..");
	            },
	            success: function success(result) {
	                trade_operation.loadingHide();
	                trade_operation.destroy();
	                trade_operation.layoutHide();
	                if (result.ret_code == 0) {
	                    return $('.sign-main').css('display', '-webkit-box').find(".balance-sign").text(result.amount);
	                }

	                if (result.ret_code == 30047) {
	                    return _trade_validation.Deal_ui.show_entry(result.retry_count, function () {
	                        trade_operation.layoutShow();
	                    });
	                }
	                if (result.ret_code == 30048) {
	                    return _trade_validation.Deal_ui.show_lock('取消', '找回密码', '交易密码已被锁定，请3小时后再试', function () {
	                        window.location = '/weixin/trade-pwd/back/?next=/weixin/recharge/';
	                    });
	                }
	                if (result.ret_code > 0) {
	                    return alert(result.message);
	                }
	            },
	            error: function error(data) {
	                if (data.status >= 403) {
	                    alert('服务器繁忙，请稍后再试');
	                }
	            },
	            complete: function complete() {
	                $submit.removeAttr('disabled').text("充值");
	            }
	        });
	    };

	    //-------------------逻辑处理
	    the_one_card();

	    $submit.on('click', function () {
	        checkOperation().then(function (result) {
	            console.log('验证成功，充值金额为' + result.amount); //check success
	            return confirm_ui(result.amount);
	        }).then(function (amount) {
	            //交易密码操作
	            trade_operation(amount);
	        }).catch(function (res) {
	            alert(res);
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
/* 7 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

	var Trade = exports.Trade = function () {
	    function Trade() {
	        var _ref = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];

	        var _ref$header = _ref.header;
	        var header = _ref$header === undefined ? '交易密码' : _ref$header;
	        var _ref$explain = _ref.explain;
	        var explain = _ref$explain === undefined ? '充值金额' : _ref$explain;
	        var _ref$done = _ref.done;
	        var done = _ref$done === undefined ? null : _ref$done;

	        _classCallCheck(this, Trade);

	        var _ref2 = [header, explain, done];
	        this.header = _ref2[0];
	        this.explain = _ref2[1];
	        this.done = _ref2[2];


	        this.$layout = $('.tran-warp');
	        this.$digt = $('.six-digt-password');
	        this.$input = null;
	        this.password = null;
	        this.rectangleWidth = null;
	        this.hash = this.hash.bind(this);
	        this.createInput = this.createInput.bind(this);
	        this.rectangleShow = this.rectangleShow.bind(this);
	        this.rectangleHide = this.rectangleHide.bind(this);
	        this.layoutHide = this.layoutHide.bind(this);
	        this.callback = this.callback.bind(this);
	        this.build();
	        this.render();
	    }

	    _createClass(Trade, [{
	        key: 'hash',
	        value: function hash() {
	            var hash = Math.random().toString(36).substr(2);
	            if ($('#' + hash).length > 0) return this.hash();
	            return hash;
	        }
	    }, {
	        key: 'createInput',
	        value: function createInput() {
	            var HASH = this.hash();
	            var input_body = '<input type=\'tel\' name=' + HASH + ' id=' + HASH + ' oncontextmenu=\'return false\' value=\'\' onpaste=\'return false\' oncopy=\'return false\' oncut=\'return false\' autocomplete=\'off\'  maxlength=\'6\' minlength=\'6\' />';
	            this.$layout.append(input_body);
	            this.$input = $('#' + HASH);
	        }
	    }, {
	        key: 'render',
	        value: function render() {
	            var _self = this;
	            $('.head-title').html(this.header);
	            $('.tran-sign').html(this.explain);

	            this.createInput();

	            this.$layout.find('.tran-close').one('click', function () {
	                _self.layoutHide();
	            });

	            this.$digt.on('click', function (e) {
	                _self.$input.focus();
	                _self.rectangleFixed('click');
	                e.stopPropagation();
	            });

	            this.$input.on('input', function () {
	                _self.rectangleFixed('input');
	            });

	            $(document).on('click', function () {
	                _self.$digt.find('i').removeClass('active');
	                _self.rectangleHide();
	            });
	        }
	    }, {
	        key: 'build',
	        value: function build() {
	            this.$input && this.$input.off('input');
	            $(document).off('click');
	            this.$digt.off('click').find('i').removeClass('active');
	            this.$layout.find('.circle').hide();
	        }
	    }, {
	        key: 'destroy',
	        value: function destroy() {
	            this.$input.val('');
	            this.$digt.find('i').removeClass('active');
	            $('.six-digt-password i ').find('.circle').hide();
	        }
	    }, {
	        key: 'rectangleFixed',
	        value: function rectangleFixed(type) {
	            var value_num = this.$input.val().length;
	            var move_space = this.rectangleWidth * value_num;
	            $('.circle').hide();

	            for (var i = 0; i < value_num; i++) {
	                $('.six-digt-password i ').eq(i).find('.circle').show();
	            }

	            this.password = this.$input.val();

	            this.rectangleShow();

	            if (value_num == 6) {
	                move_space = this.rectangleWidth * 5;
	            }

	            this.$layout.find('.blue').animate({
	                'translate3d': move_space + "px, 0 , 0"
	            }, 0);

	            if (value_num == 6) {
	                this.$digt.find('i').removeClass('active');
	                if (type == 'input') {
	                    this.rectangleHide();
	                    this.$input.blur();
	                    this.callback();
	                }
	            }

	            this.$digt.find('i').eq(value_num).addClass('active').siblings('i').removeClass('active');
	        }
	    }, {
	        key: 'rectangleShow',
	        value: function rectangleShow() {
	            this.rectangleWidth = Math.floor(this.$layout.find('.blue').width());
	            return this.$layout.find('.blue').css('visibility', 'visible');
	        }
	    }, {
	        key: 'rectangleHide',
	        value: function rectangleHide() {
	            return this.$layout.find('.blue').css('visibility', 'hidden');
	        }
	    }, {
	        key: 'loadingShow',
	        value: function loadingShow() {
	            return this.$layout.find('.tran-loading').css('display', '-webkit-box');
	        }
	    }, {
	        key: 'loadingHide',
	        value: function loadingHide() {
	            return this.$layout.find('.tran-loading').css('display', 'none');
	        }
	    }, {
	        key: 'layoutShow',
	        value: function layoutShow() {
	            return this.$layout.show();
	        }
	    }, {
	        key: 'layoutHide',
	        value: function layoutHide() {
	            return this.$layout.hide();
	        }
	    }, {
	        key: 'callback',
	        value: function callback() {
	            this.done && this.done({
	                password: this.password
	            });
	        }
	    }]);

	    return Trade;
	}();

	var Deal_ui = exports.Deal_ui = {
	    show_alert: function show_alert(state, callback, state_message) {
	        $('.tran-alert-error').show().find('.' + state).show().siblings().hide();
	        if (state_message) $('.tran-alert-error').show().find('.' + state).find('p').html(state_message);
	        $('.tran-alert-error').find('.alert-bottom').one('click', function () {
	            $('.tran-alert-error').hide();
	            callback && callback();
	        });
	        return;
	    },
	    show_entry: function show_entry(count, callback) {
	        $('.tran-alert-entry').show().find('.count_pwd').html(count);
	        $('.tran-alert-entry').find('.alert-bottom').one('click', function () {
	            $('.tran-alert-entry').hide();
	            callback && callback();
	        });
	        return;
	    },
	    show_lock: function show_lock(left, right, dec, callback) {
	        $('.tran-alert-lock').show();
	        $('.lock-close').html(left).one('click', function () {
	            $('.tran-alert-lock').hide();
	        });
	        $('.tran-alert-lock').find('.tran-dec-entry').html(dec);
	        $('.lock-back').html(right).one('click', function () {
	            callback && callback();
	        });
	    }
	};
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);