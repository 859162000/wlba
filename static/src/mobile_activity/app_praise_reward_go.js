(function(org) {

	var is_myself;
	var phone_num;

	$('#go_receive').click(function(){

		phone_num = $('#get_phone').val();
		/*申请领取*/
		$.ajax({
			url: '/weixin_activity/weixin/bonus/?act=apply&phone='+phone_num+'&wxid=1001',
			type: "GET",
		}).done(function (xhr) {
			if(xhr.err_code==0){
				window.location.href = '/weixin_activity/weixin/bonus/?wxid=1001'
			}else{
				alert(xhr.err_messege);
			}
		});
	});
	/*申请领取*/


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
		var host = 'https://www.wanglibao.com/',
			shareName = '双旦来了，翻倍狂欢',
			shareImg = host + '/static/imgs/mobile_activity/app_praise_reward/300*300.jpg',
			shareLink = host + '/activity/app_praise_reward/',
			shareMainTit = '双旦来了，翻倍狂欢',
			shareBody = '红包、加息券、体验金全部翻倍送、实物大奖同台登场，年底倾囊N重回馈。';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: '双旦来了，翻倍狂欢',
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


