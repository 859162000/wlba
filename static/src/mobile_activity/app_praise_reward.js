(function(org) {

	//alert($(window).width());

	/*滚动图*/
	function mycarousel_initCallback(carousel) {
		jQuery('.jcarousel-control a').bind('click', function() {
			carousel.scroll(jQuery.jcarousel.intval(jQuery(this).text()));
			return false;
		});
		jQuery('.jcarousel-scroll select').bind('change', function() {
			carousel.options.scroll = jQuery.jcarousel.intval(this.options[this.selectedIndex].value);
			return false;
		});
		jQuery('#mycarousel-next').bind('click', function() {
			carousel.next();
			return false;
		});
		jQuery('#mycarousel-prev').bind('click', function() {
			carousel.prev();
			return false;
		});
	};
	jQuery(document).ready(function() {
		jQuery("#mycarousel").jcarousel({
		wrap: 'circular',
		scroll: 1,
		initCallback: mycarousel_initCallback,
		buttonNextHTML: null,
		buttonPrevHTML: null
		});
	})
	/*滚动图结束*/


	//$.ajax({
	//	url: 'weixin_activity/weixin/bonus/?uid=',
	//	type: "POST",
	//	data: {
	//		//action : 'AWARD_DONE'
	//	}
	//}).done(function (xhr) {
	//
	//});

	$('#get_phone').val();
	//得到手机号

	var is_myself = false;

	$('#go_receive').click(function(){
		$('.praise_wrap').hide();
		$('.invitation_page').show();
		if(is_myself){
			$('.take_mine_reward').show();

		}else{
			$('.step_me').show();
		}
	});
	//去领取按钮

	$('.share_button').click(function(){
		$('.share_wrap').show();
	});
	$('.share_wrap').click(function(){
		$(this).hide();
	});

	$('.renovate').click(function(){
		$(this).addClass('')
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


