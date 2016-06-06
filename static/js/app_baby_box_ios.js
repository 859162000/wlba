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


$(function(){

    //设置cookie
    //分享
    var url='https://wltest.wanglibao.com/activity/app_baby_box_ios/?promo_token=bg';//获取当前的网页
    var imgsrc= 'https://wltest.wanglibao.com/static/imgs/mobile_activity/app_baby_box/300*300.jpg';
    var title = '网利宝免费萌娃礼 只为爱升温！';
    var desc = '最好的爱 只为予你';

    $.cookie('bbgz_share_url', url);
    $.cookie('bbgz_share_image_url',imgsrc);
    $.cookie('bbgz_share_title', title);
    $.cookie('bbgz_share_content', desc);
    $.cookie('share_title_wx', title);
    $.cookie('share_text_wx', desc);
    $.cookie('share_zone_wx', title);
    $.cookie('share_text_wb', title);
    $.cookie('share_copy_text', url);

    //点击分享事件
    $('#share_btn').on('click',function(){
        window.location.href = 'bbgz://bbgz.com?share';
    })
});