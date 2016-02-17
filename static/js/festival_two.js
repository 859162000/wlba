var utils = {
    getQueryString: function(name){
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]); return null;
    },
    hasQueryString: function(name){
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var r = window.location.search.substr(1).match(reg);
        if (r != null){
            return true;
        }else{
            return false;
        }
    },
    checkMobile: function(str){
        var re = /^1\d{10}$/;
        if (re.test(str)) {
            return true;
        } else {
            return false;
        }
    },
    completeChar: function(str,num){
        str = String(parseInt(str));
        var l = str.length;
        if(l < num){
            var c = num - l;
            for(var i = 0;i < c; i++){
                str = '0' + str;
            }
        }
        return str;
    }
};

var myApp ={
    //totalImages: g_resources.length,
    //loadedImages: 0,
    ajaxSwitch01: true,
    ajaxSwitch011: true,
    foodOne: 0,
    foodTwo: 0,
    remLayout: {
        switch: false,
        psdWidth: 640,
        psdHeight: 1008,
        fontSizeK: 26,
        resizeEvt: 'orientationchange' in window ? 'orientationchange' : 'resize'
    },
    windowWidth: $(window).width(),
    windowHeight: $(window).height(),
    isOnlyExternal: true,
    pages: $('.swiper-slide').size(),
    slideChangeStart: function(swiper){
        //console.log(swiper.activeIndex);
    },
    slideChangeEnd: function(swiper) {
        //console.log(swiper.activeIndex);
        //this.initArrow(swiper.activeIndex);
        //this.initPagesAnimation(swiper.activeIndex,this.pages);
        //this.initSwipeLock(swiper.activeIndex);
        switch(swiper.activeIndex)
        {
            case 0:
                break;
            case 1:
                this.initPage02();
                break;
            case 2:
                break;
            case 3:
                break;
            case 4:
                break;
            case 5:
                break;
            default:
        }
    },
    initSwipeLock: function(index){
        if(index == 3){
            myApp.mySwiper.lockSwipeToNext();
        }else if(index == 4 || index == 5){
            //console.log('ss');
            //myApp.mySwiper.lockSwipes()
            //myApp.mySwiper.lockSwipeToPrev();
        }else{
            myApp.mySwiper.unlockSwipeToNext();
        }
    },
    initArrow: function(index){
        if(index == 3 || index == 4 || index == 5){
            $('#arrow').hide();
        }else{
            $('#arrow').show();
        }
    },
    initPagesAnimation: function(index,pages){
        function handelPage(index){
            var str1 = '#panel-page0';
            var str2 = '.animation';
            for(var i = 0; i < pages; i++){
                if(i == index - 1){
                    $(str1+index+' '+str2).addClass('active');
                }else{
                    $(str1+(i + 1)+' '+str2).removeClass('active');
                }
            }
        }
        handelPage(index + 1);
    },
    audioPlay: function(){
        this.music.play();
    },
    audioPause: function(){
        this.music.pause();
    },
    audioMuted: function(){
        this.music.muted = true;
    },
    audioCancelMuted: function(){
        this.music.muted = false;
    },
    initPage01 : function(){
        setTimeout(function(){
            $('#panel-page01 .table .guideText').fadeOut(1000);
            $('#panel-page01 .table .foods').fadeIn(1000);
            $('#panel-page01 .layer03').fadeIn(1000);
        },1000);
    },
    initPage02 : function(){
        setTimeout(function(){
            $('#panel-page02 .table .guideText').fadeOut(1000);
            $('#panel-page02 .table .foods').fadeIn(1000);
            $('#panel-page02 .prompt').fadeIn(1000,function(){
                $(this).addClass('active');
            });
        },1000);
    },
    handelResult01: function(obj){
        var dom = $("#go_next");
        if(obj.ret_code == 0){
            if(!obj.is_wanglibao){
                dom.attr("href","/weixin/regist/");
            }else{
                dom.attr("href","/weixin/login/");
            }
            myApp.mySwiper.slideNext(true,1000);
        }else{
            alert(obj.message);
        }
    }
};

$(function(){

    //$('#iframe01').get(0).contentWindow.SVGDIMISOK = function(){
    //    console.log(this);  //this -> HTMLwindow
    //    console.log($('#iframe01').get(0).contentDocument); // SVGdocument
    //    console.log($('#iframe01').get(0).contentWindow); // SVGwindow
    //}


    //console.log(myApp.pages);

    //init html font-size for remLayout
    //if(myApp.remLayout.switch){
    //    console.log(myApp.windowWidth +':::'+ myApp.windowHeight);
    //    $('html').css({
    //        'font-size': myApp.windowWidth * myApp.remLayout.fontSizeK / myApp.remLayout.psdWidth
    //    });
    //
    //    $(window).on(myApp.remLayout.resizeEvt,function(){
    //        myApp.windowWidth = $(window).width();
    //        myApp.windowHeight = $(window).height();
    //        console.log(myApp.windowWidth +':::'+ myApp.windowHeight);
    //        $('html').css({
    //            'font-size': myApp.windowWidth * myApp.remLayout.fontSizeK / myApp.remLayout.psdWidth
    //        });
    //    });
    //
    //}

    //init body
    $('body').css({
        width : myApp.windowWidth,
        height: myApp.windowHeight
    });

    //微信浏览器坑爹body禁止滑动
    $('body').on('touchmove', function(){
        return false;
    });


    //main pages
    myApp.mySwiper = new Swiper('.swiper-container', {
        effect: "fade",
        fade: {
            crossFade: true
        },
        initialSlide: 0,
        direction: 'vertical',
        resistanceRatio : 0,
        noSwiping : true,
        noSwipingClass : 'swiper-no-swiping',
        onlyExternal: myApp.isOnlyExternal,
        onSlideChangeEnd: function(swiper){
            myApp.slideChangeEnd(swiper);
        },
        onSlideChangeStart: function(swiper){
            myApp.slideChangeStart(swiper);
        }
    });


    //loading  图片预加载
    //jQuery.imgpreload(g_resources, {
    //        each: function() {
    //            var status = $(this).data('loaded')?'success':'error';
    //            console.log($(this).attr('src')  + ' :: '+ status );
    //
    //            myApp.loadedImages++;
    //            var fixedP = Math.round(100 / 6 );
    //            var percent = Math.round(myApp.loadedImages / myApp.totalImages * 100);
    //
    //            var i = Math.floor( percent / fixedP);
    //            var op = Math.round(percent % fixedP / fixedP * 100);
    //
    //
    //            console.log(percent  + ' ::: ' + i + ' :::  ' + op);
    //            //$('#loading .people').eq(i-1).css({
    //            //    'opacity': 1
    //            //});
    //
    //            $('#loading .people').eq(i).css({
    //                'opacity': op/100
    //            });
    //
    //
    //
    //        },
    //        all: function() {
    //            console.log('all image loaded!!');
    //            //
    //            setTimeout(function(){
    //                $('#loading').fadeOut(1000,function(){
    //                    console.log('page01 start');
    //                })
    //            },2000);
    //            //$('#loading').fadeOut(1000,function(){
    //            //    console.log('page01 start');
    //            //})
    //        }
    //    });

    //自定义动画
    $.Velocity.RegisterUI('shanwei.fontIn',{
        defaultDuration: 300,
        calls: [
            [{opacity: [1,0]}]
        ]
    });
    var mainDelay = 100;
    var delay = 200;
    var duration = 200;
    var  seqLoading = [{
        elements: $('#loading .people').eq(0),
        properties: 'shanwei.fontIn',
        options: {delay: mainDelay, duration: duration}
    },{
        elements: $('#loading .people').eq(1),
        properties: 'shanwei.fontIn',
        options: {delay: delay, duration: duration}
    },{
        elements: $('#loading .people').eq(2),
        properties: 'shanwei.fontIn',
        options: {delay: delay, duration: duration}
    },{
        elements: $('#loading .people').eq(3),
        properties: 'shanwei.fontIn',
        options: {delay: delay, duration: duration}
    },{
        elements: $('#loading .people').eq(4),
        properties: 'shanwei.fontIn',
        options: {delay: delay, duration: duration}
    },{
        elements: $('#loading .people').eq(5),
        properties: 'shanwei.fontIn',
        options: {
            delay: delay,
            duration: duration,
            complete: function(){
                $('#loading').fadeOut(1000,function(){
                    myApp.initPage01();
                })
            }
        }
    }
    ];
    $.Velocity.RunSequence(seqLoading);


    //panel-page01
    var foodIsMoving = true;
    var posArray = ['pos-one','pos-two','pos-three','pos-four','pos-five','pos-six'];
    var activeArray = ['active01','active02','active03','active04','active05','active06'];
    $('#panel-page01 .foods .food').on('webkitAnimationEnd', function(){
        var p = parseInt($(this).attr('data-p')) - 1;
        $(this).removeClass(posArray[p]);
        $(this).addClass(posArray[(p+1)%6]);
        $(this).removeClass(activeArray[p]);

        $(this).attr({
            'data-p': (p+1)%6 +1
        });

        //确保只执行一次
        if(p == 0){
            foodIsMoving = false;
            $('#panel-page01 .myFoodBtn01').show();
            $('#panel-page01 .myFoodBtn02').hide();
        }

    });
    function startDisk(){
        $('#panel-page01 .foods .food').each(function(){
            var p = parseInt($(this).attr('data-p')) - 1;
            $(this).addClass(activeArray[p]);
        });
        foodIsMoving = true;
        $('#panel-page01 .myFoodBtn01').hide();
        $('#panel-page01 .myFoodBtn02').show();
    }

    //菜盘旋转
    var foodTimer = null;
    foodTimer = setInterval(startDisk,4500);

    //我的菜
    $('#panel-page01 .myFoodBtn01').on('touchend', function(){
        if(foodIsMoving){
            //console.log('movig');
            return false;
        }else{
            //console.log('stop');
            window.clearInterval(foodTimer);
            $(this).hide();

            $('#panel-page01 .justItBtn').show();
            $('#panel-page01 .reelectBtn').show();
            var f = parseInt($('#panel-page01 .foods .pos-one').attr('data-f')) - 1;
            $('#panel-page01 .foods .pos-one').hide();
            $('#panel-page01 .shines .shine').eq(f).show();
            $('#panel-page01 .shines').show();

        }
    });

    //重选
    $('#panel-page01 .reelectBtn').on('touchend', function(){

        $(this).hide();
        $('#panel-page01 .justItBtn').hide();
        $('#panel-page01 .myFoodBtn01').show();
        $('#panel-page01 .myFoodBtn02').hide();
        var f = parseInt($('#panel-page01 .foods .pos-one').attr('data-f')) - 1;
        $('#panel-page01 .foods .pos-one').show();
        $('#panel-page01 .shines .shine').eq(f).hide();
        $('#panel-page01 .shines').hide();

        startDisk();
        foodTimer = setInterval(startDisk,4500);
    });

    //就是它
    //var justIt = true;
    $('#panel-page01 .justItBtn').on('touchend', function(){
        //if(justIt){
            //justIt = false;
            var str = $("#redPacket1-val").val(),
                dom = $('#redPacket01'),
                html = '';
            //$.ajax({
            //    type: "POST",
            //    url: "/api/lantern/qm_reward/",
            //    dataType: "json",
            //    success: function(data){
            //        justIt = true;
            //        console.log(data);
            //        for(var i=0; i<data.rewards.length; i++){
            //            if(i != data.rewards.length-1){
            //                str += data.rewards[i]+"<br />";
            //            }else{
            //                str += data.rewards[i];
            //            }
            //
            //        }
            //        dom.find("#redPacket-cont").html(str);
            //        dom.show();
            //    },
            //    error: function(){
            //        justIt = true;
            //        alert("服务器出错了，请稍后重试");
            //    }
            //});
        str = eval('(' + str + ')');
        var redpack = str.redpack,
            coupon = str.coupon,
            experence = str.experience;
        //console.log(coupon,coupon.length);
        for(var i=0; i<redpack.length; i++){
            html += redpack[i].amount+"元红包（单笔投资满"+ redpack[i].invest_amount +"万可用）<br />";
        }
        for(var j=0; j<coupon.length; j++){
            html += coupon[j].amount+"%加息券<br />";
        }
        for(var m=0; m<experence.length; m++){
            if(m == (experence.length-1)){
                html += experence[m].amount+"元体验金";
            }else{
                html += experence[m].amount+"元体验金<br />";
            }
        }
        //console.log(html);
            dom.find("#redPacket-cont").html(html);
            dom.show();
        //}
        //var f = parseInt($('#panel-page01 .foods .pos-one').attr('data-f')) - 1;
        //var whichRed = -1;
        //switch (f){
        //    case 0:
        //        //0 鸭子 红包1
        //        whichRed = 0;
        //        break;
        //    case 1:
        //        whichRed = 1;
        //        break
        //    case 2:
        //        //2 玉米 红包1
        //        whichRed = 0;
        //        break
        //    case 3:
        //        whichRed = 1;
        //        break
        //    case 4:
        //        //4 鸡 红包1
        //        whichRed = 0;
        //        break
        //    case 5:
        //        whichRed = 1;
        //        break
        //    default:
        //        whichRed = 0;
        //}
        //switch (whichRed){
        //    case 0:
        //        $('#redPacket01').show();
        //        $('#redPacket02').hide();
        //        break;
        //    case 1:
        //        $('#redPacket01').hide();
        //        $('#redPacket02').show();
        //        break
        //    default:
        //        $('#redPacket01').show();
        //        $('#redPacket02').hide();
        //}

        //myApp.foodOne = f;
    });

    //红包收下 继续点菜
    $('.redPacket .orderBtn').on('touchend', function(){
        myApp.mySwiper.slideNext(true,1000)
    });

    //panel-page02

    //点击菜盘弹窗
    //var foodClick = true;
    $('#panel-page02 .foods .food').on('touchend', function(){
        //if(foodClick){
            //foodClick = false;
            var f = $(this).index();
            var page2 = $('#panel-page02');
            var str = $("#redPacket2-val").val(),
                html = '';
        str = eval('(' + str + ')');
            //$.ajax({
            //    type: "POST",
            //    url: "/api/lantern/hm_reward/",
            //    dataType: "json",
            //    success: function(data){
            //        foodClick = true;
            //        console.log(data);
            //        page2.find('.results .result').eq(f).show().find("div.content").html('<p class="big-tit">拿到'+ data.redpack['amount'] +'元红包啦！</p><p>单笔投资满'+ parseInt(data.redpack['invest_amount'])/10000 +'万可用</p>');
            //        page2.find('.layer03').show();
            //    },
            //    error: function(e){
            //        foodClick = true;
            //        alert('服务器连接超时，请查看您的网络！');
            //    }
            //});
        //console.log(str);
        html = '<p class="big-tit">拿到'+ str['amount'] +'元红包啦！</p><p>单笔投资满'+ parseInt(str['invest_amount'])/10000 +'万可用</p>';
            page2.find('.results .result').eq(f).show().find("div.content").html(html);
            page2.find('.layer03').show();
            //myApp.foodTwo = f;
        //}
        //console.log($(this).index());

    });

    //手机输入框切换颜色
    $('#panel-page02 #phoneNumber').on({
        'focus':function(){
            if($(this).val()=='输入手机号 领取两个红包'){
                $(this).val('');
                $(this).css({
                    'color': '#fc8910'
                });
            }
        },
        'blur':function(){
            if($(this).val()==''){
                $(this).css({
                    'color': '#cccccc'
                });
                $(this).val('输入手机号 领取两个红包');
            }
        }
    });

    //领取 AJAX 手机验证 领取
    $('#panel-page02 .receiveBtn').on('click', function(){

        if(myApp.ajaxSwitch01){
            if(myApp.ajaxSwitch011){
                var data = {
                    'phone' : $('#phoneNumber').val(),
                };

                if(data.phone == '' || data.phone == '输入手机号 领取两个红包'){
                    alert('请输入您的手机号码哦！');
                    return false;
                }
                if(utils.checkMobile(data.phone) == false){
                    alert('请输入正确的手机号码哦!');
                    return false;
                }

                myApp.ajaxSwitch01 = false;
                myApp.ajaxSwitch011 = false;
                $.ajax({
                    type: "POST",
                    url: "/api/lantern/fetch_reward/",
                    data: data,
                    dataType: "json",
                    success: function(data){
                        myApp.ajaxSwitch01 = true;
                        myApp.ajaxSwitch011 = true;
                        //console.log(data);
                        myApp.handelResult01(data);
                    },
                    error: function(e){
                        myApp.ajaxSwitch01 = true;
                        myApp.ajaxSwitch011 = true;
                        alert('服务器连接超时，请查看您的网络！');
                    }
                });
                //myApp.handelResult01({err: 0},"register");//register or 空
            }else{
                alert('您已经提交过信息了哦！');
            }
        }else{
            alert('正在提交信息哦！');
        }

    });


    //debug
    //$('#panel-page02 .results .result').on('touchend', function(){
    //    $(this).hide();
    //    $('#panel-page02 .results').hide();
    //});


    //bg_music
    $('#bg_music_img').on('touchend',function(){
        $(this).toggleClass('active');
        var oAudio =  $('#audio_bg')[0];
        //console.log( $('#audio_bg')[0].paused);
        if(oAudio.paused){
            $('#audio_bg')[0].play();
        }else{
            $('#audio_bg')[0].pause();
        }
    });

    //arrow
    //$('#arrow').on('click', function(){
    //    myApp.mySwiper.slideNext(true);
    //});

    //share
    //$('#share').on('click', function(){
    //    $(this).hide();
    //});
    function weixin_share(shareTit,fn){
        //alert(shareTit);
        var weiURL = '/weixin/api/jsapi_config/';
        var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ'];
        $.ajax({
            type: 'GET',
            url: weiURL,
            dataType: 'json',
            success: function (data) {
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
            var winHost = window.location.href;
            var host = winHost.substring(0,winHost.indexOf('/activity')),
			//var host = 'https://staging.wanglibao.com',
                shareImg = host + '/static/imgs/mobile/weChat_logo.png',
                shareLink = host + '/activity/festival_two/',
                shareMainTit = shareTit,
                shareBody = '闹元宵，吃大餐，抽红包财源滚滚来';
            //分享给微信好友
            wx.onMenuShareAppMessage({
                title: shareMainTit,
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    //alert("分享成功");
                    if(fn && (typeof fn == "function")){
                        fn();
                    }
                }
            });
            //分享给微信朋友圈
            wx.onMenuShareTimeline({
                title: shareMainTit,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    if(fn && (typeof fn == "function")){
                        fn();
                    }
                }
            });
            //分享给QQ
            wx.onMenuShareQQ({
                title: shareMainTit,
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    //alert(1);
                    if(fn && (typeof fn == "function")){
                        //alert(3);
                        fn();
                    }
                }
            })
        })
    }
	weixin_share("猴年赚不赚，就吃元宵宴");//微信分享
});