(function(){
  require.config({
    paths: {
        jquery: 'lib/jquery.min',
        'jquery.modal': 'lib/jquery.modal.min',
        'jqueryRotate' : 'jQueryRotate.2.2',
        'script' : 'sep_script',
        tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.easing' : ['jquery'],
      'jqueryRotate' : ['jquery']
    }
  });
  require(['jquery','jqueryRotate','script',"tools"], function($,jqueryRotate,easing,script,tool) {
    var gift = '',
        gift_left = 0,
        amount = '',
        amount_left = 0,
        used_chances = 3;
    var giftArr = [""];
    var giftInx;
    var dataCode = 3011;

    //ajax
    function ajaxFun(action,fun){
      $.ajax({
        type: "post",
        url: "/api/award/common_september/",
        dataType: "json",
        data: {action: action},
        success: function(data){
          if(typeof fun === "function"){
            fun(data);
          }
        }
      });
    }

    //用户抽奖信息
    function giftOk(data){
      var inx = 0;
      gift = data.gift;
      gift_left = data.gift_left;
      amount = parseInt(data.amount);
      amount_left = data.amount_left;
      used_chances = data.used_chances;
      if(amount != "None" && amount_left != 0){
        switch (amount){
          case 100:
            inx = 4;
            break;
          case 150:
            inx = 3;
            break;
          case 200:
            inx = 2;
            break;
        }
        giftArr.push(inx);
      }else{
        giftArr.push("");
      }
      if(gift != "None" && gift_left != 0){
        if(gift == "抠电影"){
          giftArr.push(1);
        }else if(gift == "爱奇艺"){
          giftArr.push(0);
        }
      }else{
        giftArr.push("");
      }
    }
    ajaxFun("ENTER_WEB_PAGE",giftOk);

    //转盘
    $(".prize-arr .rotateImg").rotate({
      bind:{
        click:function(){
		  var a;
          var $t = $(this);
          var $page = $('.page');
          var errorWin = $(".errorWin");
          var errorContent = $(".errorWin").find("#errorContent");
          var urlData = "IGNORE";
          if(used_chances >= 3 && dataCode == 3011){
            errorContent.text("您没有抽奖机会了");
            errorWin.show();
            $page.show();
            return false;
          }else if(dataCode != 3011){
            errorContent.text("您不符合参加规则");
            errorWin.show();
            $page.show();
            return false;
          }

          giftInx = Math.floor((Math.random()*giftArr.length));
          a = runzp(giftArr[giftInx]);
          if(giftArr[giftInx] > 1){
            urlData = "GET_MONEY";
          }else if(giftArr[giftInx] === 1 || giftArr[giftInx] === 0){
            urlData = "GET_GIFT";
          }else{
            urlData = "IGNORE";
          }
          //success
          ajaxFun(urlData,function(data){
            console.log(data);
          });
          $t.rotate({
            duration:3000,
            angle: 0,
            animateTo:1440+a.angle,
            easing: $.easing.easeOutSine,
            callback: function(){
              $page.show();
               used_chances++;
              $("span.chance-num").text(3 - used_chances);
              if(giftArr[giftInx] != ""){
                $('.winningDiv').show();
                $('#moeny').text(a.prize);
                var top = $('.luckDrawLeft').offset().top;
                var left = $('.luckDrawLeft').offset().left;
                $('.winningDiv').css({
                    'top': top + 10,
                    'left': left + 30
                });
              }else{
                $(".no-win").show();
              }
              $page.width(document.body.clientWidth);
              $page.height(document.body.clientHeight);
              giftArr.splice(giftInx,1);
            }
          });

		}
	  }
	});

    function closeAlert(tp){//关闭弹层
      tp.hide();
      $('.page').hide();
    }
    function backTop(){
      $('body,html').animate({scrollTop: 0}, 600);
    }
    //关闭 抽奖 遮罩\弹框
    $('.spanBtn,.againBtn').on('click',function(){
      var $t = $(this);
      var tp = $t.parents("div.alert-box");
      if(tp.length > 0){
        closeAlert(tp);
      }else{
        closeAlert($t.parents("div.winningDiv"));
      }

    });

    //返回顶部
    var topDom = $("a.xl-backtop");
    var backDom = topDom.parents("div.backtop");
    function showDom(){
      if ($(document).scrollTop() > 0) {
        backDom.addClass("show-backtop");
      } else if ($(document).scrollTop() <= 0) {
        backDom.removeClass("show-backtop");
      }
    }
    showDom();
    $(window).scroll(function () {
    showDom();
    });

    topDom.on('click',function(){
      backTop();
      return false
    });

    //中奖名单 滚动
    function scroll(){
      if (-parseInt($('#users').css('top'))>=$('#users li').height()){
        $('#users li').eq(0).appendTo($('#users'));
        $('#users').css({'top':'0px'})
        i=0
      }else{
        i++
        $('#users').css({'top':-i+'px'})
      }
    }
    var timer,i= 1,j=2;
    timer=setInterval(function(){
      scroll();
    },30);

    //返回banner处
    $(".to-register").on("click",function(){
      $('.page,.promote-register').show();
    });
    //返回banner处
    $("a.banner-register").on("click",function(){
      closeAlert($(this).parents(".alert-box"));
      backTop();
    });
    //立即注册 btn
    $(".now-register").on("click",function(){
      backTop();
    });

    //非法用户弹层
    //$("a.prize-arr").on("click",".user-no-alert",function(event){
    //  event.stopPropagation();
    //  event.preventDefault();
    //  $('.page,.errorWin').show();
    //});

    //中奖名单
    function userList(data){
      var list = data.data;
      var str = "";
      var phone,classN;
      var maxLen = 10;
      var falseList = [{"awards":"200","phone":"158******90"},{"awards":"150","phone":"134******43"},{"awards":"100","phone":"132******32"},{"awards":"100","phone":"133******34"},{"awards":"抠电影","phone":"188******24"},{"awards":"200","phone":"158******41"},{"awards":"150","phone":"188******56"},{"awards":"爱奇艺","phone":"134******67"},{"awards":"100","phone":"153******46"},{"awards":"抠电影","phone":"138******24"}]
      if(list.length<10){
        list = list.concat(falseList);
      }else{
        maxLen = list.length;
      }
      for(var i=0; i<maxLen; i++){
        phone = list[i].phone;
        if(i%2 != 0){
          classN = "winning-item";
        }else{
          classN = "winning-item even";
        }
        if(list[i].awards == "抠电影"){
          str += "<li class='"+ classN +"''>恭喜" + phone.substr(0,3)+"******"+phone.substr(phone.length-2,2) + "获得<span>抠电影代金券</span></li>";
        }else if(list[i].awards == "爱奇艺"){
          str += "<li class='"+ classN +"''>恭喜" + phone.substr(0,3)+"******"+phone.substr(phone.length-2,2) + "获得<span>爱奇艺会员</span></li>";
        }else{
          str += "<li class='"+ classN +"'>恭喜" + phone.substr(0,3)+"******"+phone.substr(phone.length-2,2) + "获得<span>" + list[i].awards +"元</span>红包</li>";
        }
      }
      $("#users").html(str);
    }
    ajaxFun("GET_AWARD",userList);

    //是否是正确渠道
    function isRoute(data){
      dataCode = data.ret_code;
      console.log(data);
      //if(dataCode != 3011){
      //  $("a.prize-arr img").removeClass("rotateImg").addClass("user-no-alert");
      //}
    }
    //是不是合法用户
    function isUser(data){
      if(data.ret_code === 3001){
        ajaxFun("IS_VALID_CHANNEL",isRoute);
      }
    }
    ajaxFun("IS_VALID_USER",isUser);

  });
}).call(this);
