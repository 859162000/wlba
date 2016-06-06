jQuery.cookie = function(name, value, options) { 
	if (typeof value != 'undefined') { 
		options = options || {}; 
		if (value === null) { 
			value = ''; 
			options.expires = -1; 
		} 
		var expires = ''; 
		if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) { 
			var date; 
			if (typeof options.expires == 'number') { 
				date = new Date(); 
				date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000)); 
			} else { 
				date = options.expires; 
			} 
			expires = '; expires=' + date.toUTCString(); 
		} 
		var path = options.path ? '; path=' + (options.path) : ''; 
		var domain = options.domain ? '; domain=' + (options.domain) : ''; 
		var secure = options.secure ? '; secure' : ''; 
		document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join(''); 
	} else { 
		var cookieValue = null; 
		if (document.cookie && document.cookie != '') { 
			var cookies = document.cookie.split(';'); 
			for (var i = 0; i < cookies.length; i++) { 
				var cookie = jQuery.trim(cookies[i]); 
				if (cookie.substring(0, name.length + 1) == (name + '=')) { 
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); 
					break; 
				} 
			} 
		} 
		return cookieValue; 
	} 
}; 


//$.cookie('bbgz_share_url', '分享地址');
//$.cookie('bbgz_share_image_url','分享缩略图');
//
//$.cookie('bbgz_share_title', '这是qq的标题');
//$.cookie('bbgz_share_content', '这是qq的描述');
//$.cookie('share_title_wx', '这是微信的标题');
//$.cookie('share_text_wx', '这是微信的描述');
//$.cookie('share_zone_wx', '这是朋友圈的分享标题');
//$.cookie('share_text_wb', '这是微博的分享标题');
//$.cookie('share_copy_text', '这是复制链接');

$.cookie('bbgz_share_url', location.protocol+"//"+location.host + '/activity/app_baby_box/?promo_token=bg');
$.cookie('bbgz_share_image_url',location.protocol+"//"+location.host + '/static/imgs/mobile_activity/app_baby_box/300*300.jpg');

$.cookie('bbgz_share_title', '网利宝免费萌娃礼 只为爱升温！');
$.cookie('bbgz_share_content', '最好的爱 只为予你');
$.cookie('share_title_wx', '网利宝免费萌娃礼 只为爱升温！');
$.cookie('share_text_wx', '最好的爱 只为予你');
$.cookie('share_zone_wx', '网利宝免费萌娃礼 只为爱升温！');
$.cookie('share_text_wb', '网利宝免费萌娃礼 只为爱升温！');
$.cookie('share_copy_text', location.protocol+"//"+location.host + '/activity/app_baby_box/?promo_token=bg');

//调起地址
//window.location.href = 'bbgz://bbgz.com?share'//ios
//window.location.href = 'bbgz://bbgz_open_owenr_sharedialog.com/'//android