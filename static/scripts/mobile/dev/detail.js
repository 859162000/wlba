webpackJsonp([3],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	/* WEBPACK VAR INJECTION */(function($) {'use strict';

	var _api = __webpack_require__(3);

	var _wx_share = __webpack_require__(10);

	(function () {
	    /**
	     * 公司信息tab
	     */
	    $('.toggleTab').on('click', function () {
	        $(this).siblings().toggle();
	        $(this).find('span').toggleClass('icon-rotate');
	    });

	    /**
	     * 倒计时
	     */
	    var countDown = $('#countDown');
	    var countDown_func = function countDown_func(target) {
	        var endTimeList = target.attr('data-left').replace(/-/g, '/');
	        var TimeTo = function TimeTo(dd) {
	            var t = new Date(dd),
	                n = parseInt(new Date().getTime()),
	                c = t - n;
	            if (c <= 0) {
	                target.text('活动已结束');
	                clearInterval(window['interval']);
	                return;
	            }
	            var ds = 60 * 60 * 24 * 1000,
	                d = parseInt(c / ds),
	                h = parseInt((c - d * ds) / (3600 * 1000)),
	                m = parseInt((c - d * ds - h * 3600 * 1000) / (60 * 1000)),
	                s = parseInt((c - d * ds - h * 3600 * 1000 - m * 60 * 1000) / 1000);
	            m < 10 ? m = '0' + m : '';
	            s < 10 ? s = '0' + s : '';
	            target.text(d + '天' + h + '小时' + m + '分' + s + '秒');
	        };
	        window['interval'] = setInterval(function () {
	            TimeTo(endTimeList);
	        }, 1000);
	    };
	    countDown.length > 0 && countDown_func(countDown);

	    /**
	     * 动画
	     */

	    $(function () {
	        var $progress = $('.progress-percent');
	        setTimeout(function () {
	            var percent = parseFloat($progress.attr('data-percent'));
	            if (percent == 100) {
	                $progress.css('margin-top', '-10%');
	            } else {
	                $progress.css('margin-top', 100 - percent + '%');
	            }
	            setTimeout(function () {
	                $progress.addClass('progress-bolang');
	            }, 1000);
	        }, 300);
	    });
	    /**
	     * 微信分享自定义
	     */
	    var weixin_share = function weixin_share() {
	        var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ'];
	        (0, _api.ajax)({
	            type: 'GET',
	            url: '/weixin/api/jsapi_config/',
	            dataType: 'json',
	            success: function success(data) {
	                //请求成功，通过config注入配置信息,
	                wx.config({
	                    debug: false,
	                    appId: data.appId,
	                    timestamp: data.timestamp,
	                    nonceStr: data.nonceStr,
	                    signature: data.signature,
	                    jsApiList: jsApiList
	                });
	            }
	        });
	        wx.ready(function () {
	            var $productName = $('.product-name'),
	                $earningRate = $('.profit-txt'),
	                $period = $('.time-txt');

	            var host = 'https://www.wanglibao.com',
	                shareName = $productName.attr('data-name'),
	                shareImg = host + '/static/imgs/mobile/share_logo.png',
	                shareLink = host + '/weixin/detail/' + $productName.attr('data-productID'),
	                shareMainTit = '我在网利宝发现一个不错的投资标的，快来看看吧',
	                shareBody = shareName + ',年收益' + $earningRate.attr('data-earn') + '%,期限' + $period.attr('data-period');
	            //分享给微信好友
	            (0, _wx_share.onMenuShareAppMessage)({
	                title: shareMainTit,
	                desc: shareBody,
	                link: shareLink,
	                imgUrl: shareImg
	            });
	            //分享给微信朋友圈
	            (0, _wx_share.onMenuShareTimeline)({
	                title: shareMainTit,
	                link: shareLink,
	                imgUrl: shareImg
	            });
	            //分享给QQ
	            (0, _wx_share.onMenuShareQQ)({
	                title: shareMainTit,
	                desc: shareBody,
	                link: shareLink,
	                imgUrl: shareImg
	            });
	        });
	    };
	    weixin_share();
	})();
	/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ },

/***/ 10:
/***/ function(module, exports) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	    value: true
	});

	var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj; };

	var _setShareData = function _setShareData(ops, suFn, canFn) {
	    var setData = {};
	    if ((typeof ops === 'undefined' ? 'undefined' : _typeof(ops)) == 'object') {
	        for (var p in ops) {
	            setData[p] = ops[p];
	        }
	    }
	    typeof suFn == 'function' && suFn != 'undefined' ? setData.success = suFn : '';
	    typeof canFn == 'function' && canFn != 'undefined' ? setData.cancel = canFn : '';
	    return setData;
	};
	/**
	 * 分享到微信朋友
	 */
	var onMenuShareAppMessage = exports.onMenuShareAppMessage = function onMenuShareAppMessage(ops, suFn, canFn) {
	    wx.onMenuShareAppMessage(_setShareData(ops, suFn, canFn));
	};
	/**
	 * 分享到微信朋友圈
	 */
	var onMenuShareTimeline = exports.onMenuShareTimeline = function onMenuShareTimeline(ops, suFn, canFn) {
	    wx.onMenuShareTimeline(_setShareData(ops, suFn, canFn));
	};

	var onMenuShareQQ = exports.onMenuShareQQ = function onMenuShareQQ() {
	    wx.onMenuShareQQ(_setShareData(ops, suFn, canFn));
	};

/***/ }

});