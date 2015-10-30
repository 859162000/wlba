require.config({
    paths: {
        'jquery.placeholder': 'lib/jquery.placeholder'
    },
    shim: {
        'jquery.placeholder': ['jquery']
    }
});
require(['jquery','jquery.placeholder'], function( $ ,placeholder) {
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
        var preInp = tp.prev("p.js-select");
        var txt = $t.text();
        var moneyStr = "";
        var dom3;
        tp.hide();
        if($t.hasClass("active")){
            return;
        }
        $t.addClass("active").siblings("a").removeClass("active");
        top.find("input").val(txt);
        preInp.show().find("input").val(txt);
        //我有车/我有房
        if(top.find("input").attr("placeholder") === "我有车/我有房"){
            if(txt === "我有房"){
                moneyStr = '<a href="javascript:;">3-50万</a><a href="javascript:;">50-100万</a><a href="javascript:;">100-300万</a><a href="javascript:;">300-500万</a>';
            }else{
                moneyStr = '<a href="javascript:;">3-10万</a><a href="javascript:;">10-30万</a><a href="javascript:;">30万以上</a>';
            }
            dom3 = tp.parents("div.select-box").siblings(".relative3");
            dom3.find("div.form-list").html(moneyStr);
            dom3.find("input.txt-input").val("");
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
            console.log(t.val());
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
        }
    }

    $("#financeSub").on("click",function (){
        var tp = $(this).parents("#financeForm");
        var doms = tp.find("input.txt-input");
        var isNext = true;
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
            console.log("submit!");
        }else{
            console.log("con't submit!");
        }
    });
});
