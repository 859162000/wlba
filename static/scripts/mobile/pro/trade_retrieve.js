webpackJsonp([3],[function(t,n,e){(function(t){"use strict";var n=function(){function t(t,n){var e=[],i=!0,r=!1,a=void 0;try{for(var o,s=t[Symbol.iterator]();!(i=(o=s.next()).done)&&(e.push(o.value),!n||e.length!==n);i=!0);}catch(l){r=!0,a=l}finally{try{!i&&s["return"]&&s["return"]()}finally{if(r)throw a}}return e}return function(n,e){if(Array.isArray(n))return n;if(Symbol.iterator in Object(n))return t(n,e);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),i=e(5),r=e(4),a=e(2),o=e(3),s=e(8);!function(){var e=t("button[type=submit]"),l=t("input[name=id_number]"),c=t("input[name=bankcard]"),u=t("input[name=cardname]"),d=[{target:l,required:!0},{target:c,required:!0},{target:u,required:!0}],h=new i.Automatic({submit:e,checklist:d});h.operationClear();var f=function(){return new Promise(function(t,e){function i(){var t=[{type:"idCard",value:l.val()},{type:"bankCard",value:c.val()},{type:"isEmpty",value:u.val()}];return(0,o.check)(t)}var r=i(),s=n(r,2),d=s[0],h=s[1];return d?t({message:"验证成功"}):((0,a.signModel)(h),e("验证失败"))})},v=function(){(0,r.ajax)({type:"get",url:"/api/pay/the_one_card/",success:function(n){var e=n.bank.name,i=n.no.slice(-4);t(".bank-name").html(e),t(".bank-card").html(i),c.attr("placeholder","**"+i+"（请输入完整卡号）"),t(".trade-warp").show()},error:function(n){t(".unbankcard").show()},complete:function(){t(".recharge-loding").hide()}})},p=function(t,n){var e=c.val(),i=l.val();(0,r.ajax)({url:"/api/trade_pwd/",type:"post",data:{action_type:3,new_trade_pwd:n,card_id:e,citizen_id:i},success:function(t){var n=(0,r.getQueryStringByName)("next");n=n=n,0==t.ret_code&&s.Deal_ui.show_alert("success",function(){window.location=n}),t.ret_code>0&&(0,a.Alert)(t.message)},complete:function(){t.loadingHide(),t.destroy(),t.layoutHide()}})},y=function(t){function n(){function i(){var i=new s.Trade({header:"请输入新交易密码",explain:"请再次确认新交易密码",done:function(r){return e.password_2=r.password,e.password_2!=e.password_1?(i.destroy(),i.layoutHide(),s.Deal_ui.show_alert("error",function(){n()})):(i.loadingShow(),void(t&&t(i,r.password)))}});i.layoutShow()}var r=new s.Trade({header:"请输入新交易密码",explain:"请设置6位数字作为新交易密码",done:function(t){e.password_1=t.password,r.destroy(),r.layoutHide(),i()}});r.layoutShow()}var e={};n()};v(),e.on("click",function(){f().then(function(){return console.log("验证成功"),y(p)})["catch"](function(t){console.log(t)})})}()}).call(n,e(1))},,function(t,n,e){(function(t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});n.Alert=function(n,e){var i=t(".wx-alert"),r=t(".wx-submit");i.css("display","-webkit-box").find(".wx-text").text(n),r.on("click",function(){i.hide(),e&&e()})},n.Confirm=function(n){var e=arguments.length<=1||void 0===arguments[1]?"确定":arguments[1],i=arguments.length<=2||void 0===arguments[2]?null:arguments[2],r=arguments.length<=3||void 0===arguments[3]?null:arguments[3],a=t(".confirm-warp");a.length<=0||(a.show(),a.find(".confirm-text").text(n),a.find(".confirm-certain").text(e),a.find(".confirm-cancel").on("click",function(){a.hide()}),a.find(".confirm-certain").on("click",function(){a.hide(),i&&(r?i(r):i())}))},n.signModel=function(n){t(".error-sign").html(n).removeClass("moveDown").addClass("moveDown").one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",function(){t(this).removeClass("moveDown")})}}).call(n,e(1))},function(t,n,e){(function(t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});var e=function(){function t(t,n){var e=[],i=!0,r=!1,a=void 0;try{for(var o,s=t[Symbol.iterator]();!(i=(o=s.next()).done)&&(e.push(o.value),!n||e.length!==n);i=!0);}catch(l){r=!0,a=l}finally{try{!i&&s["return"]&&s["return"]()}finally{if(r)throw a}}return e}return function(n,e){if(Array.isArray(n))return n;if(Symbol.iterator in Object(n))return t(n,e);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),i=(n.check=function(n){var r=null,a=null;return t.each(n,function(t,n){var o=i[n.type](n.value),s=e(o,2);return r=s[0],a=s[1],r?void 0:!1}),[r,a]},{phone:function r(n){var r=parseInt(t.trim(n)),e="请输入正确的手机号",i=new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0123456789])[0-9]{8}$/);return i.test(r)?[!0,""]:[!1,e]},password:function(n){var e="密码为6-20位数字/字母/符号/区分大小写";return 6<=t.trim(n).length&&t.trim(n).length<=20?[!0,""]:[!1,e]},rePassword:function(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],n=t.psw,e=void 0===n?null:n,i=t.repeatPsw,r=void 0===i?null:i,a="两次密码不相同";return e!==r?[!1,a]:[!0,""]},tranPassword:function(n){var e="交易密码为6位数字",i=new RegExp(/^\d{6}$/);return i.test(t.trim(n))&&!isNaN(t.trim(n))?[!0,""]:[!1,e]},bankCard:function(n){var e="银行卡号不正确",i=new RegExp(/^\d{12,20}$/);return i.test(t.trim(n))&&!isNaN(t.trim(n))?[!0,""]:[!1,e]},idCard:function(n){var e="身份证号不正确",i=new RegExp(/^([0-9]{17}([0-9]|x|X){1})|([0-9]{15})$/);return i.test(t.trim(n))?[!0,""]:[!1,e]},money100:function(t){var n="请输入100的倍数金额";return t%100===0?[!0,""]:[!1,n]},isEmpty:function(t){var n="请填写全部的表单";return""===t?[!1,n]:[!0,""]},isMoney:function(t){var n="请正确填写金额",e=1*t;return!isNaN(e)&&e>0?[!0,""]:[!1,n]}})}).call(n,e(1))},,function(t,n,e){(function(t){"use strict";function e(t){if(Array.isArray(t)){for(var n=0,e=Array(t.length);n<t.length;n++)e[n]=t[n];return e}return Array.from(t)}function i(t,n){if(!(t instanceof n))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(n,"__esModule",{value:!0});var r=function(){function t(t,n){for(var e=0;e<n.length;e++){var i=n[e];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}return function(n,e,i){return e&&t(n.prototype,e),i&&t(n,i),n}}();n.Automatic=function(){function n(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],e=t.submit,r=void 0===e?null:e,a=t.checklist,o=void 0===a?[]:a,s=t.otherlist,l=void 0===s?[]:s,c=t.done,u=void 0===c?null:c;i(this,n);var d=[r,l,o,u];this.submit=d[0],this.otherlist=d[1],this.checklist=d[2],this.callback=d[3],this.allCheck=this.allRequire(),this.canSubmit=this.canSubmit.bind(this),this.isEmptyString=this.isEmptyString.bind(this),this.isEmptyArray=this.isEmptyArray.bind(this),this.check()}return r(n,[{key:"allRequire",value:function(){var t=[].concat(e(this.checklist),e(this.otherlist));return t.filter(function(t){return!!t.required})}},{key:"isEmptyArray",value:function(t){return 0===t.length}},{key:"isEmptyString",value:function(t){return""==t}},{key:"check",value:function(){if(this.isEmptyArray(this.checklist))return console.log("checklist is none");var t=this,n=null;this.checklist.forEach(function(e){var i="select"===e.target.attr("type")?"change":"input";e.target.on(i,function(){t.style(e.target),n=t.canSubmit(),t.callback&&t.callback(n)})})}},{key:"style",value:function(n){var e=this.isEmptyString(n.val()),i=n.attr("data-icon"),r=n.attr("data-other"),a=n.attr("data-operation");e&&(""!=i&&n.siblings("."+i).removeClass("active"),""!=r&&t("."+r).attr("disabled","true"),""!=a&&n.siblings("."+a).hide()),e||(""!=i&&n.siblings("."+i).addClass("active"),""!=r&&t("."+r).removeAttr("disabled"),""!=a&&n.siblings("."+a).show())}},{key:"canSubmit",value:function(){var t="text|tel|password|select|",n=this,e=this.allCheck.every(function(e){var i=e.target;return t.indexOf(i.attr("type"))>=0?!n.isEmptyString(i.val()):t.indexOf(e.target)<0?"checkbox"==i.attr("type")&&i.prop("checked")?!0:0==e.target.length:void 0});return e?this.submit.removeAttr("disabled"):this.submit.attr("disabled","true"),e}},{key:"operationClear",value:function(){t(".wx-clear-input").on("click",function(){t(this).siblings("input").val("").trigger("input")})}},{key:"operationPassword",value:function(){t(".wx-password-operation").on("click",function(){var n=t(this).siblings("input").attr("type");"text"==n&&(t(this).siblings().attr("type","password"),t(this).addClass("wx-hide-password").removeClass("wx-show-password")),"password"==n&&(t(this).siblings().attr("type","text"),t(this).addClass("wx-show-password").removeClass("wx-hide-password"))})}}]),n}()}).call(n,e(1))},,,function(t,n,e){(function(t){"use strict";function e(t,n){if(!(t instanceof n))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(n,"__esModule",{value:!0});var i=function(){function t(t,n){for(var e=0;e<n.length;e++){var i=n[e];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}return function(n,e,i){return e&&t(n.prototype,e),i&&t(n,i),n}}();n.Trade=function(){function n(){var i=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],r=i.header,a=void 0===r?"交易密码":r,o=i.explain,s=void 0===o?"充值金额":o,l=i.done,c=void 0===l?null:l;e(this,n);var u=[a,s,c];this.header=u[0],this.explain=u[1],this.done=u[2],this.$layout=t(".tran-warp"),this.$digt=t(".six-digt-password"),this.$input=null,this.password=null,this.rectangleWidth=null,this.hash=this.hash.bind(this),this.createInput=this.createInput.bind(this),this.rectangleShow=this.rectangleShow.bind(this),this.rectangleHide=this.rectangleHide.bind(this),this.layoutHide=this.layoutHide.bind(this),this.callback=this.callback.bind(this),this.build(),this.render()}return i(n,[{key:"hash",value:function r(){var r=Math.random().toString(36).substr(2);return t("#"+r).length>0?this.hash():r}},{key:"createInput",value:function(){var n=this.hash(),e="<input type='tel' name="+n+" style='opacity:0;' id="+n+" oncontextmenu='return false' value='' onpaste='return false' oncopy='return false' oncut='return false' autocomplete='off'  maxlength='6' minlength='6' />";this.$layout.append(e),this.$input=t("#"+n)}},{key:"render",value:function(){var n=this;t(".head-title").html(this.header),t(".tran-sign").html(this.explain),this.createInput(),this.$layout.find(".tran-close").one("click",function(){n.layoutHide()}),this.$digt.on("click",function(t){n.$input.focus(),n.rectangleFixed("click"),t.stopPropagation()}),this.$input.on("input",function(){n.rectangleFixed("input")}),t(document).on("click",function(){n.$digt.find("i").removeClass("active"),n.rectangleHide()})}},{key:"build",value:function(){this.$input&&this.$input.off("input"),t(document).off("click"),this.$digt.off("click").find("i").removeClass("active"),this.$layout.find(".circle").hide()}},{key:"destroy",value:function(){this.$input.val(""),this.$digt.find("i").removeClass("active"),t(".six-digt-password i ").find(".circle").hide()}},{key:"rectangleFixed",value:function(n){var e=this.$input.val().length,i=this.rectangleWidth*e;t(".circle").hide();for(var r=0;e>r;r++)t(".six-digt-password i ").eq(r).find(".circle").show();this.password=this.$input.val(),this.rectangleShow(),6==e&&(i=5*this.rectangleWidth),this.$layout.find(".blue").animate({translate3d:i+"px, 0 , 0"},0),6==e&&(this.$digt.find("i").removeClass("active"),"input"==n&&(this.rectangleHide(),this.$input.blur(),this.callback())),this.$digt.find("i").eq(e).addClass("active").siblings("i").removeClass("active")}},{key:"rectangleShow",value:function(){return this.rectangleWidth=Math.floor(this.$layout.find(".blue").width()),this.$layout.find(".blue").css("visibility","visible")}},{key:"rectangleHide",value:function(){return this.$layout.find(".blue").css("visibility","hidden")}},{key:"loadingShow",value:function(){return this.$layout.find(".tran-loading").css("display","-webkit-box")}},{key:"loadingHide",value:function(){return this.$layout.find(".tran-loading").css("display","none")}},{key:"layoutShow",value:function(){return this.$layout.show()}},{key:"layoutHide",value:function(){return this.$layout.hide()}},{key:"callback",value:function(){this.done&&this.done({password:this.password})}}]),n}(),n.Deal_ui={show_alert:function(n,e,i){t(".tran-alert-error").show().find("."+n).show().siblings().hide(),i&&t(".tran-alert-error").show().find("."+n).find("p").html(i),t(".tran-alert-error").find(".alert-bottom").one("click",function(){t(".tran-alert-error").hide(),e&&e()})},show_entry:function(n,e){t(".tran-alert-entry").show().find(".count_pwd").html(n),t(".tran-alert-entry").find(".alert-bottom").one("click",function(){t(".tran-alert-entry").hide(),e&&e()})},show_lock:function(n,e,i,r){t(".tran-alert-lock").show(),t(".lock-close").html(n).one("click",function(){t(".tran-alert-lock").hide()}),t(".tran-alert-lock").find(".tran-dec-entry").html(i),t(".lock-back").html(e).one("click",function(){r&&r()})}}}).call(n,e(1))}]);