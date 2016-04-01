(function(org){
    var reg = /^1\d{10}$/;
    var isphone = function(date){
        if(date.ret_code == 10000){
            $(".mesg,.dialog").show();
        }else{

            if(date.message.name){
                $(".lg_name").text(date.message.name[0]);
            }
            if(date.message.address){
                $(".lg_address").text(date.message.address[0]);
            }
            if(date.message.phone){
                $(".lg_phone").text(date.message.phone[0]);
            }

        }
    };
    wlb.ready({
        app: function(mixins) {
			mixins.shareData({title: '网利宝开放日开始报名啦', content: '4月9日，与高管面对面，参观质押物，报名成功领取意外惊喜。'});

            mixins.sendUserInfo(function(data) {
				if (data.ph == '') {
                    $('#go_experience').click(function() {
					   mixins.loginApp({refresh:1, url:'https://www.wanglibao.com/activity/experience/account/'});
					})
                } else {
                    $('#go_experience').click(function() {
						window.location.href = '/activity/experience/account/';
					})
                }

				$('.button').click(function(){
					mixins.jumpToManageMoney();
				});
            });
        },
        other: function() {
			$('.button').click(function(){
				window.location.href = '/weixin/list/';
			});

			$('#go_experience').click(function() {
				window.location.href = '/activity/experience/account/';
			})

        }
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
		var host = 'https://staging.wanglibao.com/',
			shareImg = host + '/static/imgs/mobile_activity/h5_open_house/banner.jpg',
			shareLink = host + '/activity/h5_open_house/',
			shareMainTit = '网利宝开放日开始报名啦',
			shareBody = '4月9日，与高管面对面，参观质押物，报名成功领取意外惊喜。';
		//分享给微信好友
		org.onMenuShareAppMessage({
			title: shareMainTit,
			desc: shareBody,
			link: shareLink,
			imgUrl: shareImg
		});
		//分享给微信朋友圈
		org.onMenuShareTimeline({
			title: shareMainTit,
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
    var ajaxFn = function(url,option){
        org.ajax({
           type : "post",
           url : url,
           data : option,
           async : false,
           success : function(date){
               console.log(date)
               isphone(date);
           },
           error : function(){
                alert("网络出错，稍后再试");
           }
       })
    };
    var Event = function(){
        var phone = $("#phone").val(),
            name = $("#username").val(),
            address = $("#address").val();
        var opt = {"phone": phone, "name": name, "address": address};
        if(phone == ""){
            $(".lg_phone").text("*请输入手机号");
        }else if(!reg.test(phone)){
            $(".lg_phone").text("*手机号输入错误");
        }else if(strlen(name)>20){
            $(".lg_name").text("*姓名输入错误");
        }else if(strlen(address)>20){
            $(".lg_address").text("*地址输入错误");
        }else{
            ajaxFn("/api/activity_user_info/upload/",opt);
        }
    };
    function strlen(str){
        var len = 0;
        for(var i=0; i<str.length; i++){
            var c = str.charCodeAt(i);
            if ((c >= 0x0001 && c <= 0x007e) || (0xff60<=c && c<=0xff9f)) {
               len++;
             }
             else {
              len+=2;
             }
        }
        return len;
    }

    $("#login_btn").on("click",Event);
    $("#lg_uls").on("input","input",function(){
        $(this).next().text("");
    })
    $("#dia_btn").on("click",function(){
        $(".mesg,.dialog").hide();
        location.reload();
    })
})(org)