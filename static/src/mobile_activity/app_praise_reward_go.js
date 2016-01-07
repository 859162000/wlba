(function(org) {
	window.onload = function() {
		$('.fix_wrap').hide();
	};

	var url_search = window.location.search;
	var searchArray = url_search.substring(1).split("&");
	var wxid;
	var uid;
	for (var i = 0; i < searchArray.length; i++) {
		var temp = searchArray[i].split('=');
		if (temp[0] == 'wxid') {
			wxid = temp[1] ? temp[1] : '';
		}
		if (temp[0] == 'uid') {
			uid = temp[1] ? temp[1] : '';
		}
	}

	var shareName = $('.share_name').text(),
		shareImg = $('.share_img').text(),
		shareLink = $('.share_link').text(),
		shareMainTit = $('.share_title').text(),
		shareBody = $('.share_body').text(),
		share_friends = '我领到一份年终奖，'+praise_num+'元噢！你也为自己一年的努力另一份吧！，';

	var is_myself;
	var phone_num;
	/*申请领取*/
	$('#go_receive').click(function(){

		phone_num = $('#get_phone').val();

		$.ajax({
			url: '/weixin_activity/weixin/bonus/?act=apply&phone='+phone_num+'&wxid='+wxid,
			type: "GET",
		}).done(function (xhr) {
			if(xhr.err_code==0){
				window.location.href = '/weixin_activity/weixin/bonus/?wxid='+wxid
			}else{
				$('.friend_top span').text(xhr.err_messege);
				$('.friend_top').show();
			}
		});
	});
	/*申请领取*/

	$('.friend_top .close').click(function(){
		$('.friend_top').hide();
	});



    var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ'];
	org.ajax({
		type : 'GET',
		url : '/weixin/api/jsapi_config/',
		dataType : 'json',
		success : function(data) {
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
	wx.ready(function(){
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: share_friends,
			link : shareLink,
			imgUrl: shareImg
		})
		//分享给QQ
		org.onMenuShareQQ({
			title: shareMainTit,
			desc: shareBody,
			link : shareLink,
			imgUrl: shareImg
		})
	})
})(org);


