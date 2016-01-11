require.config({
    paths: {
        'jquery.placeholder': 'lib/jquery.placeholder'
    },
    shim: {
        'jquery.placeholder': ['jquery']
    }
});
require(['jquery','jquery.placeholder'], function( $ ,placeholder) {
    //表单提交  - csrf_token  start
     var  csrfSafeMethod, getCookie,sameOrigin,
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
    csrfSafeMethod = function(method) {
        return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
    };
    sameOrigin = function(url) {
        var host, origin, protocol, sr_origin;
        host = document.location.host;
        protocol = document.location.protocol;
        sr_origin = "//" + host;
        origin = protocol + sr_origin;
        return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
    };
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
              xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }
    });
    //表单提交   - csrf_token  end


    var errorDom = $("#errorBox");
    //select
    $("p.js-select").click(function(){
        var $t = $(this);
        var sib = $t.next("div.js-select-skin");
        var selectDom = $("div.select-box div.js-select-skin").not(":hidden");
        if(selectDom.length > 0){
            selectDom.hide();
        }
        if(sib.is(":hidden")){
            sib.show();
        }else{
            sib.hide();
        }
    });
    $("p.js-select-top").click(function(){
        var $t = $(this);
        var inp = $t.find("input");
        var txt = inp.attr("placeholder");
        var str;
        $t.parents("div.js-select-skin").hide();
        if(formVal.isNull(inp) === "null"){
            if(txt.indexOf("城市") > -1 || txt.indexOf("金额") > -1){
                str = "请" + txt;
            }else if(txt.indexOf("我有") > -1){
                str = "请选择我有车/我有房";
            }
            errorDom.text("* " + str).show();
        }
    });
    $("div.js-select-skin .form-list").on("click","a",function(){
        var $t = $(this);
        var tp = $t.parents("div.js-select-skin");
        var top = tp.find("p.js-select-top");
        var preBox = tp.prev("p.js-select");
        var preInp = preBox.find("input");
        var txt = $t.text();
        var moneyStr = "";
        var dom3;
        tp.hide();
        if($t.hasClass("active")){
            return;
        }
        $t.addClass("active").siblings("a").removeClass("active");
        top.find("input").val(txt);
        preBox.show();
        preInp.val(txt);
        //我有车/我有房
        if(top.find("input").attr("placeholder") === "我有车/我有房"){
            preInp.data("val",$t.data("val"));
            if(txt === "我有房" || txt === "其它"){
                moneyStr = '<a href="javascript:;">3-50万</a><a href="javascript:;">50-100万</a><a href="javascript:;">100-300万</a><a href="javascript:;">300-600万</a>';
            }else{
                moneyStr = '<a href="javascript:;">3-10万</a><a href="javascript:;">10-30万</a><a href="javascript:;">30万以上</a>';
            }
            dom3 = tp.parents("div.select-box").siblings(".relative3");
            dom3.find("div.form-list").html(moneyStr);
            dom3.find("input.txt-input").val("");
        }
        if(!errorDom.is(":hidden")){
            errorDom.html("").hide();
        }
    });
    $(document).click(function(e){
        var tag = $(e.target);
        var sel = $("div.select-box div.js-select-skin").not(":hidden");
        if(sel.length > 0) {
            if (tag.hasClass(".select-box") || tag.parents(".select-box").length > 0) {
                return;
            }else{
                sel.hide();
                sel.prev("p.js-select").show();
            }
        }
    });

    //初始化
    pageInitFun = function(){
        //文本框的得到和失去光标
        $('.placeholderInput').placeholder();
        var zhi;
        $('.placeholderInput').on("focus", function () {
            var self = $(this);
            if (self.attr('placeholder')) {
              zhi = self.attr('placeholder');
            }
            self.attr('placeholder', '');
            self.parent().addClass('selectEdLi')
        }).on('blur', function () {
            var self = $(this);
            self.attr('placeholder', zhi);
            self.parent().removeClass('selectEdLi');
            if(formVal.isNull(self) === "null"){
                errorDom.text("* "+zhi).show();
            }else if(self.hasClass("checkMobile")){
                checkMobileFun(self);
            }else{
                errorDom.hide();
            }
        });
        //Enter事件
        $(this).keydown(function(event){
            if(event.keyCode == '13'){
                $('#financeSub').trigger("click");
            }
        });
    }
    pageInitFun();

    //手机和正则
    var checkMobile = function(identifier) {  //验证手机号
      var re = /^1\d{10}$/;
      return re.test(identifier);
    }
    //验证手机号
    var checkMobileFun = function(t){
        var checkStatus = false,self = $.trim(t.val());
        if(! checkMobile(self)){
            errorDom.text('* 请输入正确手机号').show();
            checkStatus = false;
        }else{
            errorDom.text('').hide();
            checkStatus = true;
        }
        return checkStatus;
    }

    var formVal = {
        isNull: function(dom){
            var val = $.trim(dom.val());
            if(val === ""){
                return "null";
            }else{
                errorDom.hide();
            }
        },
        altShow: function(txt){
            var box = $("#alt-box");
            var altTxt = box.find("#alt-promote");
            $("#alt-pages").show();
            altTxt.text(txt);
            box.show();
            timeFun();
        }
    }
    var isSub = false;
    function fSub(self){
        isSub = true;
        var tp = self.parents("#financeForm");
        var doms = tp.find("input.txt-input");
        var isNext = true;
        var nameDom = tp.find("input.name-inp");
        var name = $.trim(nameDom.val());
        var phoneDom = tp.find("input.checkMobile");
        var phone = parseInt($.trim(phoneDom.val()));
        var cityDom = tp.find("input.city-inp");
        var city = $.trim(cityDom.val());
        var wayDom = tp.find("input.home-inp");
        var way = parseInt($.trim(wayDom.data("val")));
        var moneyDom = tp.find("input.money-inp");
        var money = $.trim(moneyDom.val());

        for(var i=0; i<doms.length; i++){
            if(formVal.isNull(doms.eq(i)) === "null"){
                errorDom.text("* "+doms.eq(i).attr("placeholder")).show();
                isNext = false;
                break;
            }else if(doms.eq(i).hasClass("checkMobile")){
                if(!checkMobileFun(doms.eq(i))){
                    isNext = false;
                    break;
                }
            }else{
               errorDom.hide();
            }
        }
        if(errorDom.is(":hidden")){
            self.text("正在提交……");
            $.ajax({
                type: "post",
                url: "/api/quick/applyer/",
                dataType: "json",
                data: {'phone': phone,'name': name,'address':city,'apply_way':way,'amount':money},
                async: true,
                success: function(data){
                    isSub = false;
                    if(self.hasClass("wx-btn")){
                        self.text("快速申请");
                    }else{
                        self.text("提交");
                    }
                    if(data.ret_code === '0'){
                        nameDom.val("");
                        phoneDom.val("");
                        cityDom.val("");
                        wayDom.val("");
                        moneyDom.val("");
                        tp.find(".form-list a").removeClass("active");
                        formVal.altShow("申请已提交，请等待业务人员联系");
                    }else if(data.ret_code === '1001'){
                        formVal.altShow("您已提交过申请，请等待业务人员联系");
                    }else if(data.ret_code === '1000'){
                        errorDom.text("* 您完整填写您的信息").show();
                    }else{
                        errorDom.text("* 系统异常，请重新提交").show();
                    }
                }
            });
        }else{
            isSub = false;
        }
    }

    $("#financeSub").on("click",function (){
        var self = $(this);
        //fSub(self);
        if(isSub){
            self.off("click");
        }else{
            self.on("click",fSub(self));
        }
    });

    function timeFun(){//倒计时
		var numDom = $("#times-box");
		var num = parseInt(numDom.text());
		var timeSet = setInterval(function(){
			if(num <= 0){
				clearInterval(timeSet);
				$("#alt-pages").hide();
                $("#alt-box").hide();
                numDom.text("3秒");
				return;
			}
			num --;
			numDom.text(num+"秒");
		},1000);
	}
});
