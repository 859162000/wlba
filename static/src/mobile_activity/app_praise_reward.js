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

	var is_animate = true;
	function title_box_animate(text){
		if(is_animate){
			is_animate = false;
			$('.title_box .text').html(text);
			$('.title_box').show().addClass('title_box_animate');
			var i = 2;
			var timer1 = setInterval(function() {
				i--;
				if (i === 0) {
					clearInterval(timer1);
					$('.title_box').removeClass('title_box_animate').hide();
					is_animate = true;
				}
			},
			1000);
		}

    }

	$.ajax({
		url: '/weixin_activity/weixin/bonus/?act=query&uid='+uid+'&wxid='+wxid,
		type: "GET",
	}).done(function (xhr) {
		
		if(xhr.err_code==0){

			renovate_friends(xhr.follow.length,xhr.follow,xhr.wx_user.is_max,xhr.wx_user.annual_bonus,xhr.wx_user.is_pay);
		}else{
			//$('.friend_top span').text(xhr.err_messege);
			//$('.friend_top').fadeIn();
		}
	});

	window.onload = function() {
		$('.fix_wrap').hide();
		var user_num = $('.swiper-slide').length;
	};

	var h5_user_static;
    org.ajax({
        url: '/api/user_login/',
        type: 'post',
        success: function(data1) {
            h5_user_static = data1.login;
        }
    });

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
		$('.regist_button,.apply_button,.login_button,.go_experience,.new_user_text').hide();
		$(this).addClass('renovate_rotate');
		$.ajax({
			url: '/weixin_activity/weixin/bonus/?act=query&uid='+uid+'&wxid='+wxid,
			type: "GET",
		}).done(function (xhr) {
			if(xhr.err_code==0){
				$('.renovate').removeClass('renovate_rotate');
				$('#praise_num').val(xhr.wx_user.annual_bonus);
				renovate_friends(xhr.follow.length,xhr.follow,xhr.wx_user.is_max,xhr.wx_user.annual_bonus,xhr.wx_user.is_pay);
				$('#zan_num').text(xhr.wx_user.good_vote);
				$('#cha_num').text(xhr.wx_user.bad_vote);
			}else{
				$('.renovate').removeClass('renovate_rotate');
				$('.friend_top span').html(xhr.err_messege);
				$('.friend_top').fadeIn();
			}
		});
	})
	/*刷新数据结束*/

	/*刷新朋友圈*/
	function renovate_friends(friends_length,friends_img,is_max,annual_bonus,is_pay){

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
		if(is_pay){
			$('.num_top').text('已领取').show();
		}else if(is_max){
			$('.num_top').text('已封顶').show();
		}
		$('#praise_num').val(annual_bonus);


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
		$('.regist_button,.apply_button,.login_button,.go_experience,.new_user_text').hide();
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=vote&type=1&uid='+uid+'&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					title_box_animate(xhr.err_messege);
					$('#praise_num').val(xhr.wx_user.annual_bonus);
					renovate_friends(xhr.follow.length,xhr.follow,xhr.wx_user.is_max,xhr.wx_user.annual_bonus,xhr.wx_user.is_pay);
					$('#zan_num').text(xhr.wx_user.good_vote);
				}else{
					title_box_animate(xhr.err_messege);
				}
			});
	});

	$('.praise_right').click(function(){
		$('.regist_button,.apply_button,.login_button,.go_experience,.new_user_text').hide();
		$.ajax({
			url: '/weixin_activity/weixin/bonus/?act=vote&type=0&uid='+uid+'&wxid='+wxid,
			type: "GET",
		}).done(function (xhr) {
			if(xhr.err_code==0){
				title_box_animate(xhr.err_messege);
				$('#praise_num').val(xhr.wx_user.annual_bonus);
				renovate_friends(xhr.follow.length,xhr.follow,xhr.wx_user.is_max,xhr.wx_user.annual_bonus,xhr.wx_user.is_pay);
				$('#cha_num').text(xhr.wx_user.bad_vote);
			}else{
				title_box_animate(xhr.err_messege);
			}
		});
	});
	/*投票结束*/

	/*申请我的年终奖*/
	var phone_number;
	$('.take_mine_button').click(function(){
		$('.regist_button,.apply_button,.login_button,.go_experience,.new_user_text').hide();
		phone_number = $('#phone_number').val();
		if($('.checkbox').hasClass('checkbox_select')){
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=apply&phone='+phone_number+'&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					window.location.href = '/weixin_activity/weixin/bonus/?wxid='+wxid;
				}else if(xhr.err_code==205){
					$('.friend_top span').html(xhr.err_messege);
					$('.friend_top').fadeIn();
					$('.apply_button').show();
				}else{
					title_box_animate(xhr.err_messege);
				}
			});
		}else{
			title_box_animate('请点击，我同意网利宝年终奖活动规则');
		}
	});
	/*申请我的年终奖结束*/

	var shareName = $('.share_name').text(),
		shareImg = $('.share_img').text(),
		shareLink = $('.share_link').text(),
		shareMainTit = $('.share_title').text(),
		shareBody = $('.share_body').text(),
		user_info = $('.user_info').text();
		share_friends = $('.share_all').text();



	if(user_info=='True'){
		$('.friend_top span').html('您已注册成功，请点击<立即使用>领用您的年终奖了');
		$('.friend_top').show();
	}else{
		if(uid!=undefined){
			//$('.shine_wrap').show();
		}
	}

	/*倒数3秒跳转体验金页面*/
	var go_experiencez_time = 3;
	function go_experience(){
		go_experiencez_time -= 1;
		if(go_experiencez_time==0){
			clearTimeout();
			if(h5_user_static){
				window.location.href = '/activity/experience/account/'
			}else{
				window.location.href = '/weixin/login/?next=/activity/experience/account/'
			}

		}
		setTimeout("go_experience()",1000);
	}
	/*倒数3秒跳转体验金页面结束*/

	/*领取我的年终奖*/
	$('.now_use').click(function(){
		$('.regist_button,.apply_button,.login_button,.go_experience,.new_user_text').hide();
		if($('.checkbox').hasClass('checkbox_select')){
			$.ajax({
				url: '/weixin_activity/weixin/bonus/?act=pay&wxid='+wxid,
				type: "GET",
			}).done(function (xhr) {
				if(xhr.err_code==0){
					$('.friend_top span').html(xhr.err_messege);
					$('.friend_top').show();
					$('.friend_top .close').hide();
					if(h5_user_static){
						$('.go_experience').show();
					}else{
						$('.login_button').show();
					}
					//go_experience();
					//倒数3秒跳转到体验金页面

				}else if(xhr.err_code==404){
					$('.regist_button').show().css('display','block');
					$('.new_user_text').show();
					$('.friend_top span').html(xhr.err_messege);
					$('.friend_top').fadeIn();

				}else if(xhr.err_code==403){
					if(h5_user_static){
						$('.go_experience').show();
					}else{
						$('.login_button').show();
					}
					$('.friend_top span').html(xhr.err_messege);
					$('.friend_top').fadeIn();
				}else{
					$('.friend_top span').html(xhr.err_messege);
					$('.friend_top').fadeIn();
				}
			});
		}else{
			$('.friend_top span').html('请点击，我同意网利宝年终奖活动规则');
			$('.friend_top').fadeIn();
		}
	});

	/*领取我的年终奖结束*/

	$('.regist_button,.apply_button,.login_button,.go_experience').hide();
	$('.regist_button').click(function(){
		window.location.href = '/weixin/regist/?next=/weixin_activity/weixin/bonus/from_regist/&promo_token=h5dianzan';
	});

	$('.apply_button').click(function(){
		window.location.href = '/weixin_activity/weixin/bonus/';
	});



	$('.login_button').click(function(){
		window.location.href = '/weixin/login/?next=/activity/experience/account/';
	});


	$('.go_experience').click(function(){
		window.location.href = '/activity/experience/account/';
	})

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


