webpackJsonp([4],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _api = __webpack_require__(3);

	var _ui = __webpack_require__(2);

	(function () {
	    var windowHeight = $(window).height(),
	        $swiperSlide = $('.swiper-slide');

	    var canGetPage = true,
	        //防止多次请求
	    FETCH_PAGE_SIZE = 10,
	        //每次请求的个数
	    FETCH_PAGE = 2,
	        AUTOPLAY_TIME = 5000,
	        //焦点图切换时间
	    LOOP = true;

	    ~function banner() {
	        if ($swiperSlide.length / 2 < 1) {
	            AUTOPLAY_TIME = 0;
	            LOOP = false;
	        }
	        var myswiper = new Swiper('.swiper-container', {
	            pagination: '.swiper-pagination',
	            loop: LOOP,
	            lazyLoading: true,
	            autoplay: AUTOPLAY_TIME,
	            autoplayDisableOnInteraction: true
	        });
	    }();

	    var fetch_data = function fetch_data() {
	        (0, _api.ajax)({
	            type: 'GET',
	            url: '/api/p2ps/wx/',
	            data: {
	                page: FETCH_PAGE,
	                pagesize: FETCH_PAGE_SIZE
	            },
	            beforeSend: function beforeSend() {
	                canGetPage = false;
	                $('.load-text').html('加载中...');
	            },
	            success: function success(data) {
	                $('#list-body').append(data.html_data);
	                FETCH_PAGE++;
	                canGetPage = true;
	            },
	            error: function error() {
	                alert('Ajax error!');
	            },
	            complete: function complete() {
	                $('.load-text').html('点击查看更多项目');
	            }
	        });
	    };
	    $('.load-body').on('click', function () {
	        canGetPage && fetch_data();
	    });
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

/***/ }
]);