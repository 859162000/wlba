webpackJsonp([0],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _automatic_detection = __webpack_require__(2);

	var auto = new _automatic_detection.Automatic({
	    submit: $('button[type=submit]'),
	    checklist: [{ target: $('input[name=username]'), required: true }, { target: $('input[name=idcard]'), required: true }]
	});

	auto.check();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },
/* 1 */,
/* 2 */
/***/ function(module, exports) {

	'use strict';

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

	        this.allCheck = [].concat(_toConsumableArray(checklist), _toConsumableArray(otherlist));

	        this.check = this.check.bind(this);
	        this.canSubmit = this.canSubmit.bind(this);
	        this.isEmptyString = this.isEmptyString.bind(this);
	        this.isEmptyArray = this.isEmptyArray.bind(this);
	    }

	    _createClass(Automatic, [{
	        key: 'isEmptyArray',
	        value: function isEmptyArray(array) {
	            if (array.length === 0) return true;
	            return false;
	        }
	    }, {
	        key: 'isEmptyString',
	        value: function isEmptyString(string) {

	            if (string == '') return true;
	            return false;
	        }
	    }, {
	        key: 'check',
	        value: function check() {
	            var _this = this;

	            if (this.isEmptyArray(this.checklist)) return console.log('checklist is none');

	            this.checklist.forEach(function (dom) {
	                console.log(_this.allCheck);
	                var _self = _this;
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
	                operation = target.attr('data-operation');

	            //等于空
	            if (isEmpty) {
	                if (icon != '') target.siblings('.' + icon).removeClass('active');
	                if (operation != '') target.siblings('.' + operation).hide();
	            }

	            //不等于空
	            if (!isEmpty) {
	                if (icon != '') target.siblings('.' + icon).addClass('active');
	                if (operation != '') target.siblings('.' + operation).show();
	            }
	        }
	    }, {
	        key: 'canSubmit',
	        value: function canSubmit() {}
	    }]);

	    return Automatic;
	})();

/***/ }
]);