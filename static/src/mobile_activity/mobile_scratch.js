org.canvas = (function(org){
    var lib = {
        init :function(){
            lib._drawing();
            lib.Registered();
            lib.iSAndiOS();
        },
        _drawing:function(){
            var bodyStyle = document.body.style;

            bodyStyle.mozUserSelect = 'none';
            bodyStyle.webkitUserSelect = 'none';

            var img = new Image(),idx= 3,
                canvas = document.querySelector('canvas'),
                spans=document.getElementById("spans"),
                min=document.getElementById("main"),
                $portunity=$("#opportunity"),
                demo=document.getElementById("demo").getElementsByTagName("img")[0],
                str = ["100元现金红包","150元现金红包","200元现金红包","爱奇艺会员","扣电影代金券","抽前吼三吼，大奖跟我走","红包何时有，把酒问青天","大奖下回见，网利宝天天见","佛说：前世500次回眸才能换得一次中奖，淡定"],
                num,text,used_chances,clsName,dataCode,total,
                end=false,cls=false,down=false,mousedown = false,
                gift="None",
                gift_left=0,
                amount="None",
                amount_left= 0,
                i = 0,ss,
                clicks= 1,
                timer=null,
                dataArr = [],
                retCode,
                urlData;


            canvas.style.backgroundColor='transparent';
            canvas.style.position = 'absolute';
            canvas.style.left = 0;
            canvas.style.top = 0;
            img.src = "/static/imgs/mobile_activity/app_scratch/gg_guajiang.png";
            $("#continue").hide();
            //判断用户是否登录
            function jugde(){
                clsName=$("#untub").attr("className");
                if(clsName=="scratch_tub"){
                    text="注册帐号后即可刮奖";
                    spans.innerHTML=text;
                }else if(clsName=="unAuthenticated"){
                    if(!cls){
                       $portunity.html("点击开始即可刮奖");
                    }
                    $("#btn_go").on("click",function(){
                        down=true;                        Interface();
                        //evendrawImg();
                        if(used_chances<=3){
                            ss=idx-used_chances;
                            $portunity.html("您有"+ss+"次刮奖机会");
                        }
                        $(this).hide().next().show();
                        cls=true;
                    })
                }
            }
            //渲染蒙层
            img.addEventListener('load',evendrawImg);
            jugde();
            function evendrawImg(e){
                var ctx;
                var w = demo.width,
                    h = demo.height;

                function layer(ctx) {
                    ctx.drawImage(img,0,0,w,h);
                }
                //当手指移动的时候
                function eventMove(e){
                    e.preventDefault();
                    if(mousedown && cls) {
                         if(e.changedTouches) e=e.changedTouches[e.changedTouches.length-1];
                         var x = (e.clientX + document.body.scrollLeft || e.pageX) - min.offsetLeft || 0,
                             y = (e.clientY + document.body.scrollTop || e.pageY) - min.offsetTop-min.scrollHeight+20 || 0;
                         with(ctx) {
                             beginPath();
                             arc(x, y, 20, 0, Math.PI * 2);
                             fill();
                         }
                    }
                }
                function timers(){
                    ctx.drawImage(img,0,0,w,h);
                }
                canvas.width=w;
                canvas.height=h;
                ctx=canvas.getContext('2d');
                layer(ctx);
                ctx.globalCompositeOperation = 'destination-out';
                canvas.addEventListener('touchmove', eventMove);
                canvas.addEventListener('mousemove', eventMove);
                return function(){
                    return ctx.drawImage(img,0,0,w,h);
                };
            }
                //当手指按下的时候
            function eventDown(e){
                e.preventDefault();
                if(down == true) Ignoreate();
                mousedown=true;
                end=true;
                clearInterval(timer);

            }
            //当手指松开的时候
            function eventUp(e){
                e.preventDefault();
                i++;
                mousedown=false;
                down=false;
                clearInterval(timer);
                text=spans.innerHTML;
                ss=idx-used_chances;
                if(cls){
                    timer=setInterval(function(){
                        timers();
                    },2000);
                }
                if(amount != 'None' && amount_left != 0 && clicks==1 || gift_left!=0 && gift!="None"&& clicks==1) $("#continue").html("领奖");
                if(used_chances<3){
                    $portunity.html("您有"+ss+"次刮奖机会");
                }
                if(used_chances == 3)$portunity.html("您的刮奖次数已用完");

            }
            canvas.addEventListener('touchstart', eventDown);
            canvas.addEventListener('touchend', eventUp);
            canvas.addEventListener('mousedown', eventDown);
            canvas.addEventListener('mouseup', eventUp);
            $("#continue").on('click',function(){
                if(end)
                    porttunclick();
            });
            function porttunclick(){
                if(used_chances<3){
                    if($("#continue").html()=="领奖"){
                        $("#dask").css({"display":"block"});
                        $("#delog").find("h3").html(text+"已发送！请留意站内信！");
                        $("#close,#ok").on('click',function(){
                            $("#dask").css({"display":"none"});
                            $("#continue").html("再来一次");
                            clicks=2;
                            evendrawImg()();
                        })
                    }else{
                        Interface();
                        evendrawImg();
                        i=0;
                        end=false;
                        clicks=1;
                        down=true;
                    }
                    clearInterval(timer);
                }else if (dataCode != 3011 && clsName=="unAuthenticated") {
                    spans.innerHTML = "您不符合参加规则";
                } else if(clsName=="scratch_tub"){
                    spans.innerHTML = "注册帐号后即可刮奖";
                }else{
                    //evendrawImg();
                   $portunity.html("您的刮奖次数已用完");
                   spans.innerHTML = "您的刮奖次数已用完";
                }
            }
            //ajax请求数据
            function ajaxFun(action, fun) {
                org.ajax({
                    type: "post",
                    url: "/api/award/common_september/",
                    dataType: "json",
                    data: {action: action},
                    async: false,
                    success: function (data) {
                        if (typeof fun === "function") {
                            fun(data);
                            console.log(data);
                        }
                    }
                });
            }
            function Ignoreate(){
                 function rotateFun(data) {
                    used_chances = data.used_chances;
                    retCode = data.ret_code;
                 }
                if (amount != 'None' && amount_left != 0) {
                    urlData = "GET_MONEY";
                    //dataArr.shift();
                } else if (gift != 'None' && gift_left != 0) {
                    urlData = "GET_GIFT";
                    //dataArr.shift();
                } else {
                    urlData = "IGNORE";
                }

                ajaxFun(urlData, rotateFun);
                console.log(dataArr+"  "+urlData)
            }
            function Interface(){

                //判断是否为正确渠道
                function isChannel(data) {
                    dataCode = data.ret_code;
                }
                //判断是否为合法渠道
                function isUser(data) {
                    if (data.ret_code === 3001) {
                        ajaxFun("IS_VALID_CHANNEL", isChannel);
                        if(dataCode===3011){
                            isdataCode();
                        }else{
                            spans.innerHTML = "您不符合参加规则";
                        }
                    }
                }
                ajaxFun("IS_VALID_USER", isUser);

                //用户抽奖信息
                function isdataCode(){
                    function lotterInfo(data) {
                        gift = data.gift;
                        gift_left = data.gift_left;
                        used_chances = data.used_chances;
                        amount = parseInt(data.amount);
                        amount_left = data.amount_left;
                        total=data.total_chances;

                    }
                    ajaxFun("ENTER_WEB_PAGE", lotterInfo);
                    if (retCode == 3024 && dataCode == 3011 && used_chances > 2) {
                        spans.innerHTML = "您的刮奖次数已用完";
                        $portunity.html("您的刮奖次数已用完");
                    }else {
                        if(amount != 'None' && amount_left != 0){
                            console.log(amount)
                            spans.innerHTML = amount+"元现金红包";
                        }else if(gift != 'None' && gift_left != 0){
                            console.log(gift+"  "+gift_left);
                            if (gift == "抠电影") {
                                spans.innerHTML="抠电影代金券";
                            } else if (gift == "爱奇艺") {
                                spans.innerHTML="爱奇艺会员";
                            }
                        }else{
                            num = Math.floor(5+Math.random()*3);
                            text=str[num];
                            spans.innerHTML=text;
                        }
                    }
                }
            }
        },
        Registered:function(){
            //判断输入的手机号是否正确
            $("#scratch_btn").on('click',function(e){
                var val=$("#zctext").val();
                e.preventDefault();
                if(val==""){
                    alert("请输入手机号");
                }else if(!/^1{1}[3578]{1}\d{9}$/.test(val)){
                    alert("请输入正确的手机号");
                }else{
                    window.location.href="/weixin/regist/?next=/activity/app_scratch/&phone="+val;
                }
            })
        },
        //判断是否是iOS
        iSAndiOS:function(){
            var u = navigator.userAgent, app = navigator.appVersion;
            var isiOS = !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
            if(isiOS) $("#textbox").append("<span>6.</span><p>网利宝对此活动享有最终解释权。与苹果公司（Apple Inc）无关，如有疑问请联系在线客服或拨打400-588-066</p>");
        }
    }
    return {
        init : lib.init
    }
})(org);
;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if( src ){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);