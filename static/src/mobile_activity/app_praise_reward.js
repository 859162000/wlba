(function(org) {

	//alert($(window).width());

	var is_myself;

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

	var is_myself = false;

	/*去领取按钮*/
	$('#go_receive').click(function(){
		$('.praise_wrap').hide();
		$('.invitation_page').show();
		if(is_myself){
			$('.take_mine_reward').show();

		}else{
			$('.step_me').show();
		}
	});
	/*去领取按钮*/

	/*分享*/
	$('.share_button').click(function(){
		$('.share_wrap').show();
	});
	$('.share_wrap').click(function(){
		$(this).hide();
	});
	/*结束分享*/

	/*刷新数据*/
	$('.renovate').click(function(){
		$(this).addClass('renovate_rotate');
		$.ajax({
			url: 'weixin_activity/weixin/bonus/?uid='+uid+'&wxid='+wxid,
			type: "POST",
			data: {

			}
		}).done(function (xhr) {
			if(xhr.err_code==0){
				$(this).removeClass('renovate_rotate');
			}else if(xhr.err_code==0){
				alert('信息错误')
			}
		});
	})
	/*刷新数据结束*/

	/*同意活动规则按钮*/
	$('.checkbox').click(function(){
		if($(this).hasClass('checkbox_select')){
			$(this).removeClass('checkbox_select');
		}else{
			$(this).addClass('checkbox_select');
		}
	});
	/*同意活动规则按钮结束*/

	/*邀请好友弹窗关闭*/
	$('.share_wrap .close').click(function(){
		$('.share_wrap').hide();
	});
	/*邀请好友弹窗关闭结束*/

	var praise_num;
	/*投票*/
	$('.praise_left').click(function(){

		$('#praise_num').val();
		if(praise_num>=30000){
			$('.friend_top span').text('您的朋友已获取全额年终奖');
			$('.friend_top').fadeIn();
		}else{
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=vote&type=1&uid='+uid+'&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
					$('.float').show().addClass('float_animate');
				}else{
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
				}
			});
		}
	});

	$('.praise_right').click(function(){
		if(praise_num<=100){
			$('.friend_top span').text('给您的朋友留点年终奖吧');
			$('.friend_top').fadeIn();
		}else{
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=vote&type=2&uid='+uid+'&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
					$('.float').show().addClass('float_animate');
				}else{
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
				}
			});
		}
	});
	/*投票结束*/

	/*领取我的年终奖*/
	var phone_number;
	$('.take_mine_button').click(function(){
		phone_number = $('#phone_number').val();
		if($('.checkbox').hasClass('checkbox_select')){
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=apply&phone='+phone_number+'&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					window.location.href = '/weixin_activity/weixin/bonus/?wxid=1002'
				}else{
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
				}
			});
		}else{
			$('.friend_top span').text('请点击，我同意网利宝年终奖活动规则');
			$('.friend_top').fadeIn();
		}
	});
	/*领取我的年终奖结束*/

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


