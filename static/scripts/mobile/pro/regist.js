webpackJsonp([6],[function(t,e,n){(function(t){"use strict";var e=function(){function t(t,e){var n=[],r=!0,i=!1,a=void 0;try{for(var o,c=t[Symbol.iterator]();!(r=(o=c.next()).done)&&(n.push(o.value),!e||n.length!==e);r=!0);}catch(s){i=!0,a=s}finally{try{!r&&c["return"]&&c["return"]()}finally{if(i)throw a}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),r=n(5),i=n(4),a=n(2),o=n(3),c=n(8);!function(){function n(e){var n=t.trim(h.val());return new Promise(function(t,r){(0,i.ajax)({url:e,type:"POST",data:{identifier:u.val(),password:v.val(),captcha_0:d.val(),captcha_1:l.val(),validate_code:f.val(),invite_code:""===n?g.val():n,invite_phone:""},beforeSend:function(){s.text("注册中,请稍等...").attr("disabled","true")},success:function(e){t(e)},error:function(t){r(t)},complete:function(){s.text("立即注册 ｜ 领取奖励").removeAttr("disabled")}})})}var s=t("button[type=submit]"),u=t("input[name=identifier]"),l=t("input[name=captcha_1]"),d=t("input[name=captcha_0]"),f=t("input[name=validate_code]"),v=t("input[name=password]"),h=t("input[name=invite_code]"),p=t("input[name=agreement]"),m=t("#captcha"),y=t("button[name=validate_operation]"),g=t("#token"),b=[{target:u,required:!0},{target:l,required:!0},{target:f,required:!0},{target:v,required:!0},{target:h,required:!1}],w=new r.Automatic({submit:s,checklist:b,otherlist:[{target:p,required:!0}],done:function(){k.status()&&y.attr("disabled",!0)}});w.operationClear(),w.operationPassword();var k=(0,c.validation)(u,d,l,m);k.render(),t("#agreement").on("click",function(){t(this).toggleClass("agreement"),t(this).hasClass("agreement")?p.attr("checked","checked"):p.removeAttr("checked"),u.trigger("input")});var x=t(".xieyi-btn"),A=t(".cancel-xiyie"),S=t(".regist-protocol-div");x.on("click",function(t){t.preventDefault(),S.css("display","block"),setTimeout(function(){S.css("top","0%")},0)}),A.on("click",function(){S.css("top","100%"),setTimeout(function(){S.css("display","none")},200)});var _=function(){return new Promise(function(t,n){function r(){var t=[{type:"phone",value:u.val()},{type:"isEmpty",value:l.val()},{type:"isEmpty",value:f.val()},{type:"password",value:v.val()}];return(0,o.check)(t)}var i=r(),c=e(i,2),s=c[0],d=c[1];return s?t("验证成功"):((0,a.signModel)(d),console.log("验证失败"))})};s.on("click",function(){_().then(function(t){return console.log(t),n("/api/register/")}).then(function(t){console.log("register success"),0===t.ret_code&&(0,a.Alert)("注册成功",function(){var t=""==(0,i.getQueryStringByName)("next")?"/weixin/regist/first/":(0,i.getQueryStringByName)("next");t=""==(0,i.getQueryStringByName)("mobile")?t:t+"&mobile="+(0,i.getQueryStringByName)("mobile"),t=""==(0,i.getQueryStringByName)("serverId")?t:t+"&serverId="+(0,i.getQueryStringByName)("serverId"),window.location.href=t}),t.ret_code>0&&(0,a.signModel)(t.message)})["catch"](function(t){var e=JSON.parse(t.responseText);429===t.status?(0,a.signModel)("系统繁忙，请稍候重试"):(0,a.signModel)(e.message)})})}()}).call(e,n(1))},,function(t,e,n){(function(t){"use strict";Object.defineProperty(e,"__esModule",{value:!0});e.Alert=function(e,n){var r=t(".wx-alert"),i=t(".wx-submit");r.css("display","-webkit-box").find(".wx-text").text(e),i.on("click",function(){r.hide(),n()})},e.Confirm=function(e){var n=arguments.length<=1||void 0===arguments[1]?"确定":arguments[1],r=arguments.length<=2||void 0===arguments[2]?null:arguments[2],i=arguments.length<=3||void 0===arguments[3]?null:arguments[3],a=t(".confirm-warp");a.length<=0||(a.show(),a.find(".confirm-text").text(e),a.find(".confirm-certain").text(n),a.find(".confirm-cancel").on("click",function(){a.hide()}),a.find(".confirm-certain").on("click",function(){a.hide(),r&&(i?r(i):r())}))},e.signModel=function(e){t(".error-sign").html(e).removeClass("moveDown").addClass("moveDown").one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",function(){t(this).removeClass("moveDown")})}}).call(e,n(1))},function(t,e,n){(function(t){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=function(){function t(t,e){var n=[],r=!0,i=!1,a=void 0;try{for(var o,c=t[Symbol.iterator]();!(r=(o=c.next()).done)&&(n.push(o.value),!e||n.length!==e);r=!0);}catch(s){i=!0,a=s}finally{try{!r&&c["return"]&&c["return"]()}finally{if(i)throw a}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),r=(e.check=function(e){var i=null,a=null;return t.each(e,function(t,e){var o=r[e.type](e.value),c=n(o,2);return i=c[0],a=c[1],i?void 0:!1}),[i,a]},{phone:function i(e){var i=parseInt(t.trim(e)),n="请输入正确的手机号",r=new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0123456789])[0-9]{8}$/);return r.test(i)?[!0,""]:[!1,n]},password:function(e){var n="密码为6-20位数字/字母/符号/区分大小写";new RegExp(/^\d{6,20}$/);return 6<t.trim(e).length&&t.trim(e).length<20?[!0,""]:[!1,n]},rePassword:function(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],e=t.psw,n=void 0===e?null:e,r=t.repeatPsw,i=void 0===r?null:r,a="两次密码不相同";return n!==i?[!1,a]:[!0,""]},tranPassword:function(e){var n="交易密码为6位数字",r=new RegExp(/^\d{6}$/);return r.test(t.trim(e))&&!isNaN(t.trim(e))?[!0,""]:[!1,n]},bankCard:function(e){var n="银行卡号不正确",r=new RegExp(/^\d{12,20}$/);return r.test(t.trim(e))&&!isNaN(t.trim(e))?[!0,""]:[!1,n]},idCard:function(e){var n="身份证号不正确",r=new RegExp(/^([0-9]{17}([0-9]|x|X){1})|([0-9]{15})$/);return r.test(t.trim(e))?[!0,""]:[!1,n]},money100:function(t){var e="请输入100的倍数金额";return t%100===0?[!0,""]:[!1,e]},isEmpty:function(t){var e="请填写全部的表单";return""===t?[!1,e]:[!0,""]},isMoney:function(t){var e="请正确填写金额",n=1*t;return!isNaN(n)&&n>0?[!0,""]:[!1,e]}})}).call(e,n(1))},,function(t,e,n){(function(t){"use strict";function n(t){if(Array.isArray(t)){for(var e=0,n=Array(t.length);e<t.length;e++)n[e]=t[e];return n}return Array.from(t)}function r(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(e,"__esModule",{value:!0});var i=function(){function t(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}return function(e,n,r){return n&&t(e.prototype,n),r&&t(e,r),e}}();e.Automatic=function(){function e(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],n=t.submit,i=void 0===n?null:n,a=t.checklist,o=void 0===a?[]:a,c=t.otherlist,s=void 0===c?[]:c,u=t.done,l=void 0===u?null:u;r(this,e);var d=[i,s,o,l];this.submit=d[0],this.otherlist=d[1],this.checklist=d[2],this.callback=d[3],this.allCheck=this.allRequire(),this.canSubmit=this.canSubmit.bind(this),this.isEmptyString=this.isEmptyString.bind(this),this.isEmptyArray=this.isEmptyArray.bind(this),this.check()}return i(e,[{key:"allRequire",value:function(){var t=[].concat(n(this.checklist),n(this.otherlist));return t.filter(function(t){return!!t.required})}},{key:"isEmptyArray",value:function(t){return 0===t.length}},{key:"isEmptyString",value:function(t){return""==t}},{key:"check",value:function(){if(this.isEmptyArray(this.checklist))return console.log("checklist is none");var t=this,e=null;this.checklist.forEach(function(n){var r="select"===n.target.attr("type")?"change":"input";n.target.on(r,function(){t.style(n.target),e=t.canSubmit(),t.callback&&t.callback(e)})})}},{key:"style",value:function(e){var n=this.isEmptyString(e.val()),r=e.attr("data-icon"),i=e.attr("data-other"),a=e.attr("data-operation");n&&(""!=r&&e.siblings("."+r).removeClass("active"),""!=i&&t("."+i).attr("disabled","true"),""!=a&&e.siblings("."+a).hide()),n||(""!=r&&e.siblings("."+r).addClass("active"),""!=i&&t("."+i).removeAttr("disabled"),""!=a&&e.siblings("."+a).show())}},{key:"canSubmit",value:function(){var t="text|tel|password|select|",e=this,n=this.allCheck.every(function(n){var r=n.target;return t.indexOf(r.attr("type"))>=0?!e.isEmptyString(r.val()):t.indexOf(n.target)<0?"checkbox"==r.attr("type")&&r.prop("checked")?!0:0==n.target.length:void 0});return n?this.submit.removeAttr("disabled"):this.submit.attr("disabled","true"),n}},{key:"operationClear",value:function(){t(".wx-clear-input").on("click",function(){t(this).siblings("input").val("").trigger("input")})}},{key:"operationPassword",value:function(){t(".wx-password-operation").on("click",function(){var e=t(this).siblings("input").attr("type");"text"==e&&(t(this).siblings().attr("type","password"),t(this).addClass("wx-hide-password").removeClass("wx-show-password")),"password"==e&&(t(this).siblings().attr("type","text"),t(this).addClass("wx-show-password").removeClass("wx-hide-password"))})}}]),e}()}).call(e,n(1))},,,function(t,e,n){(function(t){"use strict";Object.defineProperty(e,"__esModule",{value:!0}),e.validation=void 0;var r=function(){function t(t,e){var n=[],r=!0,i=!1,a=void 0;try{for(var o,c=t[Symbol.iterator]();!(r=(o=c.next()).done)&&(n.push(o.value),!e||n.length!==e);r=!0);}catch(s){i=!0,a=s}finally{try{!r&&c["return"]&&c["return"]()}finally{if(i)throw a}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),i=n(4),a=n(2),o=n(3);e.validation=function c(e,n,s,u){function c(){var e="/captcha/refresh/?v="+(new Date).getTime();t.get(e,function(t){u.attr("src",t.image_url),n.val(t.key)})}function l(){function t(t,e,n){return new Promise(function(r,a){(0,i.ajax)({url:"/api/phone_validation_code/"+t+"/",data:{captcha_0:e,captcha_1:n},type:"POST",beforeSend:function(){h.attr("disabled","disabled").text("发送中..")},success:function(){r("短信已发送，请注意查收！")},error:function(t){var e=JSON.parse(t.responseText);return h.removeAttr("disabled").text("获取验证码"),clearInterval(v),v=null,c(),a(e.message)}})})}function u(t){return new Promise(function(e,n){var r=function(){return t>1?(t--,h.text(t+"秒后可重发")):(clearInterval(v),v=null,h.text("重新获取").removeAttr("disabled"),c(),n("倒计时失效，请重新获取"))};return r(),v=setInterval(r,1e3)})}function l(e,n,r){d(e).then(function(){return console.log("验证成功"),t(e,n,r)}).then(function(t){(0,a.signModel)(t),console.log("短信发送成功");var e=60;return u(e)})["catch"](function(t){(0,a.signModel)(t)})}var d=function(t){return new Promise(function(e,n){function i(){var e=[{type:"phone",value:t}];return(0,o.check)(e)}var a=i(),c=r(a,2),s=c[0],u=c[1];return s?e("验证成功"):n(u)})};h.on("click",function(){var t=e.val(),r=n.val(),i=s.val();l(t,r,i)})}function d(){v&&(clearInterval(v),h.removeAttr("disabled").text("获取验证码"))}function f(){return!!v}var v=null,h=t("button[name=validate_operation]");return c(),u.on("click",function(){c()}),{render:l,status:f,destory:d,validation:c}}}).call(e,n(1))}]);