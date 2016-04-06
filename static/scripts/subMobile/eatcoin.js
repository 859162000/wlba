getCookie = function(name) {
    var cookie, cookieValue, cookies, i;
    cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        cookies = document.cookie.split(";");
        i = 0;
        while (i < cookies.length) {
            cookie = $.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
            i++;
        }
    }
    return cookieValue;
};
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        //if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        //}
    }
});
$(function(){
    var box = $('#box');
    box.css('width',window.innerWidth);
    box.css('height',window.innerHeight);
    var B = 0.56;
    var canvasObj = $('#canvas');//获取页面画布元素
    var ca=document.getElementById("canvas");//获取画布元素
    var ctx=ca.getContext("2d");//设定画布为2d展示
    var bj1=new Image();//定义背景对象
    var player=new Image();//定义人的对象
    var tu=new Array();//定义金币的对象
    bj1.src="/static/imgs/sub_weixin/eatcoin/bj.png";//为背景设置图片
    player.src="/static/imgs/sub_weixin/eatcoin/monkeyPending.gif";//为人物设置图片
    var playerWidth =window.innerWidth*0.347;//285;//*B;//人物的宽度
    var playerHeight =window.innerHeight*0.325;//*B;//人物的高度
    var h=20;
    var sudu = 30;
    var zl=100;
    var chi=0;
    var shi=0;
    var fs=0;
    var bj=bj1;
    function object(){
        this.x=0;
        this.y=0;
        this.l=11;
        this.image=new Image();
    }
    var sprite=new object();
    sprite.x=(window.innerWidth/2-window.innerWidth/4)-playerWidth/2;
    sprite.y=window-playerHeight;
    sprite.image=player;
    addListener(ca,"touchstart",m);//监控鼠标
    var zh_x = [(window.innerWidth/2+window.innerWidth/4)-105*0.5/2,(window.innerWidth/2-window.innerWidth/4)-105*0.5/2];
    function isLogin(){
        $.ajax({
            type:"post",
            url:"/api/user_login/",
            dataType:"json",
            success:function(data){
                if(data.login==true){
                    $(".iphone input").css("display","none");
                }
            }
        })
    }
    function isRegister(phone){
        var isreg;
        $.ajax({
            type:"get",
            async:false,
            url:"/api/user_exists/"+phone+"/",
            dataType:"json",
            //success:function(data){
            //    return data.existing;
            //}
        }).done(function(data){
            isreg = data.existing;
        });
        return isreg;
    }
    function chansheng(){
        if(shi%h==0){
            for(var j=2*chi;j<2*(chi+1);j++){
                //alert("@@@")
                tu[j]=new object();
                var i=zh_x[Math.round(Math.random()*1)];
                if(j==2*chi+1)
                {
                    while(Math.abs(i-tu[2*chi].x)<30){
                        i=zh_x[Math.round(Math.random()*1)];
                    }
                }
                var k=Math.round(Math.random()*zl);
                if(k < 80){
                    tu[j].image.src="/static/imgs/sub_weixin/eatcoin/jinbi.png";
                    tu[j].q = 1;
                }else{
                    if(tu1) {
                        if(tu1.q==1) {
                            tu[j].image.src = "/static/imgs/sub_weixin/eatcoin/bomb.gif";
                            tu[j].q = 2;
                        }else {
                            tu[j].image.src="/static/imgs/sub_weixin/eatcoin/jinbi.png";
                            tu[j].q = 1;
                        }
                    }
               }
                tu[j].x=i;
                tu[j].y=-100;
                var tu1 = tu[j];
            }
           chi++;
            if(chi==10) chi=0;
        }
        shi++;
    }
    function draw(){
        chansheng();
        for(var i=0;i<tu.length;i++){
            if(jianche(sprite,tu[i])) {
                if(tu[i].q == 1){
                    $(".number").html(fs+=1);
                    h = 5;
                   if(sudu<80) {
                        sudu += 2;
                   }
                }else if(tu[i].q == 2){
                    $(".monkeyPending").attr("src","/static/imgs/sub_weixin/eatcoin/zl.gif");
                    ca.removeEventListener("touchstart",m);
                    stop();
                    setTimeout(function(){
                        $("#box").hide();
                        $(".reward_page").css("display","block");
                        gm();
                        $(".logo").show();
                        var jl = $(".number").text()
                        $(".jbsl").text(jl);
                        if(jl>=0&&jl<=5){
                            jp = "66元";
                        }else if(jl>=6&&jl<=10){
                            jp = "166元";
                        }else if(jl>=11&&jl<=15){
                            jp = "566元";
                        }else if(jl>=16){
                            jp = "666元";
                        }
                        var conten = "我用幸运猴接了"+$(".number").html()+"个金币，快来试试你能接多少个吧！";
                        fxApi(conten);
                        $('.jp').text(jp);
                        tu = [];
                        isLogin();
                    },1000);
                }
                if(tu[i]) {
                    tu[i].y += 300;
                }
            }else if(!jianche(sprite,tu[i])){
                if(tu[i]){
                    if(tu[i].y>window.innerHeight){
                        tu.splice(i,1);
                    }else {
                        tu[i].y += sudu;
                    }
                }
            }
            if(tu[i]) {
                if(tu[i].q == 2){
                    ctx.drawImage(tu[i].image, tu[i].x, tu[i].y-52.5, 105*0.5, 105*0.5);
                }else{
                    ctx.drawImage(tu[i].image, tu[i].x, tu[i].y, 105*0.5, 105*0.5);
                };
            }
        }
    }
    function gm(){
        var opacity = 0;
        var gmElem = $(".gm img");
        var gmInterval = setInterval(function(){
            gmElem.toggle();
            if($(".fx").is(":hidden")&&$(".lq").is(":hidden")){
                clearInterval(gmInterval);
            }
        },500)
    }
    function jianche(a,b){
        if(b){
            var c=a.x-b.x;//猴子的横坐标-金币的横坐标
            var d=a.y-b.y;//猴子的纵坐标-金币的纵坐标
            if(Math.abs(c)<window.innerWidth/4&& b.y+b.image.height*0.5>(window.innerHeight-playerHeight)&& b.y<window.innerHeight){
                return true;
            }else{
                return false;
            }
        }else{
            return false;
        }
    }
    function addListener(element,e,fn){
        if(element.addEventListener){
            element.addEventListener(e,fn,false);
        } else {
            element.attachEvent("on" + e,fn);
        }
    }
    function m(event){
        var windowX = window.innerWidth;
        console.log(event.targetTouches[0]);
        if(event.targetTouches[0].clientX>windowX/2){
            sprite.x = (windowX/4*3)-playerWidth/2;
        }else{
            sprite.x = (windowX/4)-playerWidth/2;
        }
        $(".monkeyPending").css("left",sprite.x);
    }
    function stop(){
        clearInterval(interval);
    }
    function start(){
        var js = 3;
        var djs = setInterval(function(){
            if(js>1) {
                js--;
                $(".djs").find("span").text(js)
            }else{
                clearInterval(djs);
                $(".blank").hide();
                $(".djs").hide();
                $(".sz").hide();
               interval = setInterval(function(){
                    ctx.clearRect(0,0,window.innerWidth,window.innerHeight);
                    ctx.drawImage(bj,0,0,window.innerWidth,window.innerHeight);
                    //ctx.drawImage(sprite.image,sprite.x,sprite.y,playerWidth,playerHeight);
                    draw();
                },100);
            }
        },1000)
    }
    function fxApi(conten){
        var winHot = window.location.protocol+"//"+window.location.host;
        var link = window.location.href;
        var img = winHot+"/static/imgs/sub_weixin/eatcoin/wx_logo.jpg";
        var tit = "天降福利 幸运来袭";
        wx.onMenuShareAppMessage({
            title: tit, // 分享标题
            desc: conten,//"我用幸运猴接了"+$(".number").html()+"个金币，快来试试你能接多少个吧！",//conten, // 分享描述
            link: link, // 分享链接
            imgUrl: img, // 分享图标
            type: 'link', // 分享类型,music、video或link，不填默认为link
            dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
            success: function () {
                alert("分享成功")
                // 用户确认分享后执行的回调函数
            },
            cancel: function () {
                alert("分享已取消")
                // 用户取消分享后执行的回调函数
            }
        });
        wx.onMenuShareTimeline({
            title: tit, // 分享标题
            link: winHot, // 分享链接
            imgUrl: img, // 分享图标
            success: function () {
                alert("分享成功")
                // 用户确认分享后执行的回调函数
            },
            cancel: function () {
                alert("分享已取消")
                // 用户取消分享后执行的回调函数
            }
        });
        wx.onMenuShareQQ({
            title: tit, // 分享标题
            desc: conten, // 分享描述
            link:winHot, // 分享链接
            imgUrl: img, // 分享图标
            success: function () {
                alert("分享成功")
                // 用户确认分享后执行的回调函数
            },
            cancel: function () {
                alert("分享已取消")
                // 用户取消分享后执行的回调函数
            }
        });
        wx.onMenuShareWeibo({
            title: tit, // 分享标题
            desc: conten, // 分享描述
            link: link, // 分享链接
            imgUrl: img, // 分享图标
            success: function () {
                alert("分享成功")
                // 用户确认分享后执行的回调函数
            },
            cancel: function () {
                alert("分享已取消")
                // 用户取消分享后执行的回调函数
            }
        });
    }
    $(document).ready(function() {
        setTimeout(function () {
            $(window).scrollTop(1);
        }, 0);
        document.getElementById('car_audio').play();
        document.addEventListener("WeixinJSBridgeReady", function () {
            WeixinJSBridge.invoke('getNetworkType', {}, function (e) {
                document.getElementById('car_audio').play();
            });
        }, false);
        var cunt = 0;

       // $("img").load(function(){
        //   console.log(immgInx+1);
        //    if(immgInx++==imgNum){
        //       if(cunt==0) {
         //          alert(imgNum);
                   var progress = setInterval(function () {
                       $(".loaded").css("background-size", cunt * 10 + "%" + " " + "100%");
                       if (cunt == 11) {
                           clearInterval(progress);
                           $(".loadding_page").hide();
                           $(".start_page").show();
                       }else{
                           cunt++;
                       }
                   }, 500);
         //      }
        //    }
        //});
        document.ontouchmove = function(e){
            e.preventDefault();
        }
        $(".again_btn").bind("click",function(){
            $(".reward_page").hide();
            $("#box").show();
            $(".blank").show();
            $(".sz").show();
            $(".djs").show();
            addListener(ca,"touchstart",m);
            $(".monkeyPending").attr("src","/static/imgs/sub_weixin/eatcoin/monkeyPending.gif");
            $(".logo").hide();
            $(".number").text("0");
            fs = 0;
            h = 20;
            sudu = 30;
            $(".djs span").text(3);
            start();
        });

        $(".instructions a").bind("click",function(e){
            e.stopPropagation();
            $(".bounced").show();
            $(".blank").show();
        });

        $(".bounced .close").bind("click",function(){
            $(".bounced").hide();
            $(".blank").hide();
        });

        $(".play_btn").bind("click",function(){
            $(".start_page").hide();
            $("#box").show();
            $(".blank").show();
            sprite.x = (window.innerWidth/2-window.innerWidth/4)-playerWidth/2;
            sprite.y = window.innerHeight-playerHeight;
            $(".monkeyPending").css("left",sprite.x+"px");
            $(".monkeyPending").css("top",sprite.y+"px");
            $("canvas").attr('width',window.innerWidth+"px");
            $("canvas").attr('height',window.innerHeight+"px");
            $(".logo").hide();
            start();
        });

        $(".get_reward_btn").bind("click",function(){
            var total = $(".jbsl").text();
            if($(".iphone input").is(":hidden")){
                var param={"total":total};
                lqjl(param);
            }else{
                var phone = $(".iphone input").val();
                if(phone && /^1[2|3|4|5|8|7|]\d{9}$/.test(phone)){
                    var param = {"total":total,"phone":phone};
                    if(isRegister(phone)){
                        lqjl(param);
                    }else{
                        $(".blank").show();
                        $(".yz_tc").show();
                        $(".phone input").val(phone);
                        sxyzm();
                    }
                } else{
                    alert("请输入正确的手机号");
                }
            }
        });

        function sxyzm(){
            $.ajax({
                type:"get",
                url:"/anti/captcha/refresh/",
                data:{key:new Date().getTime()},
                dataType:"json",
                success:function(data){
                    $(".img_yzm img").attr("src",data.image_url);
                    $(".img_yzm img").attr("key",data.key);
                }
            })
        }
        function lqjl(param){
            $.ajax({
                type:"post",
                url:"/api/activity/happy_monkey/",
                data:param,
                dataType:"json",
                success : function(data) {
                    if(data.ret_code==0){
                        $(".lq").hide();
                        $(".fx").show();
                        $(".blank").hide();
                    }else if(data.ret_code=1001){
                        alert("每个用户一天只能领取一次奖励");
                    }else{
                        alert(data.message);
                    }
                }
            })
        }
        $(".sx").click(function(){
            sxyzm();
        });
        $(".hqdx input").click(function(){
            $(this).attr("disabled","disabled");
            $(this).css("background-image","url(/static/imgs/sub_weixin/eatcoin/un_get_note.png)");
            var dxsj = 60;
            var phone = $(".yz_tc .phone input").val();
            var param = {"captcha_0":$(".img_yzm img").attr("key"),"captcha_1":$(".input_yzm input").val()};
            $(this).hide().siblings().show();
            var self = this
            var djs = setInterval(function(){
                if(dxsj==1){
                    $(self).removeAttr("disabled");
                    $(self).css("background-image","url(/static/imgs/sub_weixin/eatcoin/get_note.png)");
                    $(self).show().siblings().hide();
                    $(self).siblings().text(60);
                    clearInterval(djs);
                }else{
                    dxsj--
                    $(self).siblings().text(dxsj);
                }

            },1000)
            $.ajax({
                type:"post",
                url:"/api/phone_validation_code/register/"+phone+"/",
                data:param,
                dataType:"json",
                success:function(data){
                    //console.log(data);
                },
                error:function(data){
                    //var message = new Function("return "+data.responseText)();
                    //alert(message.message);
                    //alert(eval("(" + data.responseText+ ")").message);
                    alert(data.responseText.split(":")[1].split('"')[1]);
                    //if(eval("(" + data.responseText+ ")").message=="图片验证码错误"){
                        sxyzm();
                        $(".input_yzm input").val();
                        $(self).removeAttr("disabled");
                        $(self).css("background-image","url(/static/imgs/sub_weixin/eatcoin/get_note.png)");
                        $(self).show().siblings().hide();
                        $(self).siblings().text(60);
                        clearInterval(djs);
                   // };
                    //alert(eval("(" + data.responseText+ ")").message);
                }
            })
        })
        $(".srdx input").bind('input propertychange',function(){
            if($(this).val()!=""&&$(".phone input").val()!=""&&$(".input_yzm input").val()!=""){
                $(".dllq img").attr("src","/static/imgs/sub_weixin/eatcoin/dl_lq.png")
            }
        });
        $(".dllq").click(function(){
            var img = $(this).find("img").attr("src").split("/");
            if(img[img.length-1]=="dl_lq.png"){
                var IGNORE_PWD = "YES";
                var identifier = $(".yz_tc .phone input").val();
                var validate_code = $(".srdx input").val();
                var promo_token="fwhyx";
                var param={"IGNORE_PWD":IGNORE_PWD,"identifier":identifier,"validate_code":validate_code,"promo_token":promo_token};
                $.ajax({
                    type:"post",
                    url:"/api/register/",
                    data:param,
                    dataType:"json",
                    success:function(result){
                        if(result.ret_code==0){
                            var total = $(".jbsl").text();
                            var param = {"total":total,"phone":identifier};
                            lqjl(param);
                        }else{
                            alert(result.message);
                        }
                    }
                })
            };
        })
        $(".phone input,.input_yzm input").bind('input propertychange',function(){
            if($(".phone input").val().length!=0&&$(".input_yzm input").val().length!=0){
                $(".hqdx input").removeAttr("disabled");
                $(".hqdx input").css("background-image","url(/static/imgs/sub_weixin/eatcoin/get_note.png)");
            }
        })
        $(".srdx input").bind('input propertychange',function(){
            if($(this).val()!=""){
                $(".dllq input").removeAttr("disabled");
                $(".dllq input").css("background-image","url(/static/imgs/sub_weixin/eatcoin/dl_lq.png)")
            }
        });
        $(".fx_btn").bind("click",function(){
            $(".blank").show();
            $(".fxts").show();
        });
        $(".m").bind("click",function(){
            $(this).find(".stop").toggle();
            if($(this).find(".stop").css("display")=="block"){
                document.getElementById("car_audio").pause();// =true;
            }else{
                document.getElementById("car_audio").play(); //= false;
            }
        });
        $(".yz_tc .close").click(function(){
            $(".blank").hide();
            $(this).parent().hide();
        })
        window.addEventListener('orientationchange', function(event){
            if( window.orientation == 90 || window.orientation == -90 ) {
                alert("请保持竖屏");
            }
        });
        $.ajax({
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
                    jsApiList: ["onMenuShareAppMessage","onMenuShareTimeline","onMenuShareQQ","onMenuShareWeibo"]
                });
            }
        });
        wx.ready(function(){
            var conten = "我用幸运猴接了"+$(".number").html()+"个金币，快来试试你能接多少个吧！";
            fxApi(conten);
        })
    })
});