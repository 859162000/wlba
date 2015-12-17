webpackJsonp([0],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _automatic_detection = __webpack_require__(2);

	var auto = new _automatic_detection.Automatic({
	    submit: $('button[type=submit]'),
	    checklist: [{ target: $('input[name=password]'), required: true }, { target: $('input[name=phone]'), required: true }, { target: $('input[name=validation]'), required: true }],
	    otherlist: [{ target: $('select[name=bank]'), required: true }]
	});

	auto.check();
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
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ }
]);