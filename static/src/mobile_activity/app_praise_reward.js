(function(org) {

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

	$.ajax({
		url: '/weixin_activity/weixin/bonus/?act=query&uid='+uid+'&wxid='+wxid,
		type: "GET",
	}).done(function (xhr) {
		if(xhr.err_code==0){
			renovate_friends(xhr.follow.length,xhr.follow);
			//$('.renovate').click();
		}else{
			//$('.friend_top span').text(xhr.err_messege);
			//$('.friend_top').fadeIn();
		}
	});

	if(uid!=undefined){
		$('.shine_wrap').show();
	}

	window.onload = function() {
		$('.fix_wrap').hide();
		var user_num = $('.swiper-slide').length;

	};

	var is_myself = false;

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
			url: '/weixin_activity/weixin/bonus/?act=query&uid='+uid+'&wxid='+wxid,
			type: "GET",
		}).done(function (xhr) {
			if(xhr.err_code==0){
				$('.renovate').removeClass('renovate_rotate');
				$('#praise_num').val(xhr.wx_user.annual_bonus);
				renovate_friends(xhr.follow.length,xhr.follow);
			}else{
				$('.renovate').removeClass('renovate_rotate');
				$('.friend_top span').text(xhr.err_messege);
				$('.friend_top').fadeIn();
			}
		});
	})
	/*刷新数据结束*/

	/*刷新朋友圈*/
	function renovate_friends(friends_length,friends_img){
		var str='';
		var follow_one='';
		for(var i=0; i<friends_length; i++){
			follow_one = friends_img[i];
			str +='<div class="swiper-slide"><img class="user" src="'+follow_one.from_headimgurl+'"/></div>'
		}

		var swiper = new Swiper('.swiper-container', {
			initialSlide : 0,
			slidesPerView: 6,
			nextButton: '.swiper-button-next',
			prevButton: '.swiper-button-prev',
			loop: false
		});
		swiper.removeAllSlides();
		swiper.appendSlide(str);
		swiper.update();
		swiper.slideTo(0, 100, false);

	}
	/*刷新朋友圈结束*/
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

	var praise_num = $('#praise_num').val();
	/*投票*/
	$('.praise_left').click(function(){

			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=vote&type=1&uid='+uid+'&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
					$('.float').text('+100').show().addClass('float_animate');
					$('#praise_num').val(xhr.wx_user.annual_bonus);
					renovate_friends(xhr.follow.length,xhr.follow);
				}else{
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
				}
			});
	});

	$('.praise_right').click(function(){
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=vote&type=2&uid='+uid+'&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
					$('.float').text('-100').show().addClass('float_animate');
					$('#praise_num').val(xhr.wx_user.annual_bonus);
					renovate_friends(xhr.follow.length,xhr.follow);
				}else{
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
				}
			});
	});
	/*投票结束*/

	/*申请我的年终奖*/
	var phone_number;
	$('.take_mine_button').click(function(){
		phone_number = $('#phone_number').val();
		if($('.checkbox').hasClass('checkbox_select')){
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=apply&phone='+phone_number+'&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					window.location.href = '/weixin_activity/weixin/bonus/?wxid='+wxid;
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
	/*申请我的年终奖结束*/

	/*领取我的年终奖*/
	$('.now_use').click(function(){
		if($('.checkbox').hasClass('checkbox_select')){
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=pay&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					$('.friend_top span').text(xhr.err_messege);
					$('.friend_top').fadeIn();
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

	$('.shine_wrap .close').click(function(){
		$('.shine_wrap').hide();
	});

	$('.rule').click(function(){
		$('.rule_wrap').show();
	});
	$('.rule_wrap .close').click(function(){
		$('.rule_wrap').hide();
	});

	var shareName = $('.share_name').text(),
		shareImg = $('.share_img').text(),
		shareLink = $('.share_link').text(),
		shareMainTit = $('.share_title').text(),
		shareBody = $('.share_body').text(),
		share_friends = '我领到一份年终奖，'+praise_num+'元噢！你也为自己一年的努力另一份吧！，';

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


