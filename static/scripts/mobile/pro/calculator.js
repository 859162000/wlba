webpackJsonp([16],[function(n,i,t){(function(n){"use strict";var i=t(4),o=t(2);!function(){var t=n("input[data-role=p2p-calculator]"),e=n(".calculator-buy"),c=n(".count-input"),a=void 0,l=void 0,d=void 0;t.on("input",function(){i.calculate.operation(n(this))}),e.on("click",function(){return a=n(this).attr("data-productid"),d=c.val(),l=n("#expected_income").text(),d%100!==0||""==d?(0,o.signModel)("请输入100的整数倍"):void(window.location.href="/weixin/view/buy/"+a+"/?amount="+d)})}()}).call(i,t(1))},,function(n,i,t){(function(n){"use strict";Object.defineProperty(i,"__esModule",{value:!0});i.Alert=function(i,t){var o=n(".wx-alert"),e=n(".wx-submit");o.css("display","-webkit-box").find(".wx-text").text(i),e.on("click",function(){o.hide(),t&&t()})},i.Confirm=function(i){var t=arguments.length<=1||void 0===arguments[1]?"确定":arguments[1],o=arguments.length<=2||void 0===arguments[2]?null:arguments[2],e=arguments.length<=3||void 0===arguments[3]?null:arguments[3],c=n(".confirm-warp");c.length<=0||(c.show(),c.find(".confirm-text").text(i),c.find(".confirm-certain").text(t),c.find(".confirm-cancel").on("click",function(){c.hide()}),c.find(".confirm-certain").on("click",function(){c.hide(),o&&(e?o(e):o())}))},i.signModel=function(i){n(".error-sign").html(i).removeClass("moveDown").addClass("moveDown").one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",function(){n(this).removeClass("moveDown")})}}).call(i,t(1))}]);