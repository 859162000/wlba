webpackJsonp([9],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	__webpack_require__(2);

	var _received_ui = __webpack_require__(13);

	var _api = __webpack_require__(3);

	(function () {
	    var renderDetail = function renderDetail(result) {
	        var slide = [],
	            $item = $('.received-list');
	        slide.push((0, _received_ui.detail)(result));
	        $item.append(slide.join(''));
	        $('.received-loding').hide();
	    };

	    var fetch = function fetch(product_id) {
	        (0, _api.ajax)({
	            url: '/api/home/p2p/amortization/' + product_id,
	            type: 'get',
	            success: function success(result) {
	                renderDetail(result);
	            }
	        });
	    };

	    var render = function render() {
	        var product_id = (0, _api.getQueryStringByName)('productId');
	        fetch(product_id);
	    };

	    render();
	})();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },

/***/ 2:
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

/***/ 13:
/***/ function(module, exports) {

	"use strict";

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	var slide = exports.slide = function slide(data) {
	    var slide = "<div class='swiper-slide received-slide'>";
	    slide += "<div class='received-slide-date'>" + data.term_date.slice(0, 4) + "年" + data.term_date.slice(5, 7) + "月</div>";
	    slide += "<div class='received-slide-data'>";
	    slide += "<div class='received-data-list'>";
	    slide += "<span class='received-left-center'>";
	    slide += "<div class='data-name'>回款总额(元)</div>";
	    if (data.total_sum == 0) {
	        slide += "<div class='data-value'>0.00</div>";
	    } else {
	        slide += "<div class='data-value'>" + data.total_sum + "</div>";
	    }
	    slide += "</span>";
	    slide += "</div>";
	    slide += "<div class='received-data-list'>";
	    slide += "<span class='received-left-center'>";
	    slide += "<div class='data-name'>回款笔数</div>";
	    if (data.term_date_count == 0) {
	        slide += "<div class='data-value'>0</div>";
	    } else {
	        slide += "<div class='data-value'>" + data.term_date_count + "</div>";
	    }
	    slide += "</span>";
	    slide += "</div>";
	    slide += "</div>";
	    slide += "</div>";

	    return slide;
	};

	var list = exports.list = function list(data) {
	    var list = "<a href='/weixin/received/detail/?productId=" + data.product_id + "' class='received-list'>";
	    list += "<div class='list-head-warp'>";
	    list += "<div class='list-head arrow'>";
	    list += "<div class='head-space'>&nbsp&nbsp</div>";
	    list += "<span class='head-name'>" + data.product_name + "</span>";
	    list += "<span class='head-process'>" + data.term + "/" + data.term_total + "</span>";
	    list += "</div></div>";

	    list += "<div class='list-cont'>";
	    list += "<div class='list-flex'>";
	    list += "<div class='cont-grey-2'>" + data.term_date.slice(0, 10) + "</div>";
	    list += "<div class='cont-grey-1'>回款日期</div>";
	    list += "</div>";
	    list += "<div class='list-flex'>";
	    list += "<div class='cont-red'>" + data.principal + "</div>";
	    list += "<div class='cont-grey-1'>本(元)</div>";
	    list += "</div>";

	    list += "<div class='list-flex'>";
	    list += "<div class='cont-red'>" + data.total_interest + "</div>";
	    list += "<div class='cont-grey-1'>息(元)</div>";
	    list += "</div>";

	    list += "<div class='list-flex'>";
	    list += "<div class='cont-grey-2'>" + data.settlement_status + "</div>";
	    if (data.settlement_status == '提前回款') {
	        list += "<div class='cont-grey-1'>" + data.settlement_time.slice(0, 10) + "</div>";
	    }
	    list += "</div>";
	    list += "</div>";
	    list += "</div></a>";
	    return list;
	};

	var detail = exports.detail = function detail(data) {
	    var detail = "<div class='list-head-warp'>";
	    detail += "<div class='list-head'>";
	    detail += "<div class='head-space'>&nbsp&nbsp</div>";
	    detail += "<span class='head-name head-allshow'>" + data.equity_product_short_name + "</span>";
	    detail += "</div></div>";

	    detail += "<div class='list-nav'>";
	    detail += "<ul><li class='item-date'>时间</li><li>本金(元)</li><li>利息(元)</li><li class='item-count'>总计(元)</li></ul>";
	    detail += "</div>";
	    detail += "<div class='detail-space-grep'></div>";

	    for (var i = 0; i < data.amortization_record.length; i++) {

	        detail += "<div class='detail-list'>";
	        detail += "<div class='detail-item item-date'>" + data.amortization_record[i].amortization_term_date.slice(0, 10) + "</div>";
	        detail += "<div class='detail-item'>" + data.amortization_record[i].amortization_principal + "</div>";
	        detail += "<div class='detail-item'>" + data.amortization_record[i].amortization_amount_interest;
	        if (data.amortization_record[i].amortization_coupon_interest > 0) {
	            detail += "<span>+</span><span class='blue-text'>" + data.amortization_record[i].amortization_coupon_interest + "</span><span class='blue-sign'>加息</span>";
	        }
	        detail += "</div>";
	        detail += "<div class= 'detail-item item-count'>" + data.amortization_record[i].amortization_amount + "</div>";
	        if (data.amortization_record[i].amortization_status == '提前回款' || data.amortization_record[i].amortization_status == '已回款') {
	            detail += "<div class= 'repayment-icon'></div>";
	        }
	        detail += "</div>";
	    }

	    return detail;
	};

/***/ }

});