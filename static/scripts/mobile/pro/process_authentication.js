webpackJsonp([7],[function(t,n,e){(function(t){"use strict";var n=function(){function t(t,n){var e=[],r=!0,i=!1,a=void 0;try{for(var o,s=t[Symbol.iterator]();!(r=(o=s.next()).done)&&(e.push(o.value),!n||e.length!==n);r=!0);}catch(u){i=!0,a=u}finally{try{!r&&s["return"]&&s["return"]()}finally{if(i)throw a}}return e}return function(n,e){if(Array.isArray(n))return n;if(Symbol.iterator in Object(n))return t(n,e);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),r=e(5),i=e(4),a=e(2),o=e(3);!function(){var e=t("button[type=submit]"),s=t("input[name=name]"),u=t("input[name=idcard]"),c=[{target:s,required:!0},{target:u,required:!0}],l=new r.Automatic({submit:e,checklist:c});l.operationClear();var d=function(){return new Promise(function(t,e){function r(){var t=[{type:"isEmpty",value:s.val()},{type:"idCard",value:u.val()}];return(0,o.check)(t)}var i=r(),c=n(i,2),l=c[0],d=c[1];return l?t("验证成功"):((0,a.signModel)(d),console.log("验证失败"))})},f=function(t,n){return new Promise(function(r,a){(0,i.ajax)({type:"POST",url:t,data:n,beforeSend:function(){e.attr("disabled",!0).text("认证中，请等待...")},success:function(t){r(t)},error:function(t){a(t)},complete:function(){e.removeAttr("disabled").text("实名认证")}})})};e.on("click",function(){d().then(function(t){return console.log(t),f("/api/id_validate/",{name:s.val(),id_number:u.val()})}).then(function(t){return console.log("success"),"true"==!t.validate?(0,a.Alert)("认证失败，请重试"):void(0,a.Alert)("实名认证成功!",function(){return window.location.href="/weixin/regist/second/"})})["catch"](function(t){var n=JSON.parse(t.responseText);return 8!=n.error_number?(0,a.Alert)(n.message):void(0,a.Alert)(n.message,function(){window.location.href="/weixin/list/"})})})}()}).call(n,e(1))},,function(t,n,e){(function(t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});n.Alert=function(n,e){var r=t(".wx-alert"),i=t(".wx-submit");r.css("display","-webkit-box").find(".wx-text").text(n),i.on("click",function(){r.hide(),e()})},n.Confirm=function(n){var e=arguments.length<=1||void 0===arguments[1]?"确定":arguments[1],r=arguments.length<=2||void 0===arguments[2]?null:arguments[2],i=arguments.length<=3||void 0===arguments[3]?null:arguments[3],a=t(".confirm-warp");a.length<=0||(a.show(),a.find(".confirm-text").text(n),a.find(".confirm-certain").text(e),a.find(".confirm-cancel").on("click",function(){a.hide()}),a.find(".confirm-certain").on("click",function(){a.hide(),r&&(i?r(i):r())}))},n.signModel=function(n){t(".error-sign").html(n).removeClass("moveDown").addClass("moveDown").one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",function(){t(this).removeClass("moveDown")})}}).call(n,e(1))},function(t,n,e){(function(t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});var e=function(){function t(t,n){var e=[],r=!0,i=!1,a=void 0;try{for(var o,s=t[Symbol.iterator]();!(r=(o=s.next()).done)&&(e.push(o.value),!n||e.length!==n);r=!0);}catch(u){i=!0,a=u}finally{try{!r&&s["return"]&&s["return"]()}finally{if(i)throw a}}return e}return function(n,e){if(Array.isArray(n))return n;if(Symbol.iterator in Object(n))return t(n,e);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),r=(n.check=function(n){var i=null,a=null;return t.each(n,function(t,n){var o=r[n.type](n.value),s=e(o,2);return i=s[0],a=s[1],i?void 0:!1}),[i,a]},{phone:function i(n){var i=parseInt(t.trim(n)),e="请输入正确的手机号",r=new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0123456789])[0-9]{8}$/);return r.test(i)?[!0,""]:[!1,e]},password:function(n){var e="密码为6-20位数字/字母/符号/区分大小写";return 6<=t.trim(n).length&&t.trim(n).length<20?[!0,""]:[!1,e]},rePassword:function(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],n=t.psw,e=void 0===n?null:n,r=t.repeatPsw,i=void 0===r?null:r,a="两次密码不相同";return e!==i?[!1,a]:[!0,""]},tranPassword:function(n){var e="交易密码为6位数字",r=new RegExp(/^\d{6}$/);return r.test(t.trim(n))&&!isNaN(t.trim(n))?[!0,""]:[!1,e]},bankCard:function(n){var e="银行卡号不正确",r=new RegExp(/^\d{12,20}$/);return r.test(t.trim(n))&&!isNaN(t.trim(n))?[!0,""]:[!1,e]},idCard:function(n){var e="身份证号不正确",r=new RegExp(/^([0-9]{17}([0-9]|x|X){1})|([0-9]{15})$/);return r.test(t.trim(n))?[!0,""]:[!1,e]},money100:function(t){var n="请输入100的倍数金额";return t%100===0?[!0,""]:[!1,n]},isEmpty:function(t){var n="请填写全部的表单";return""===t?[!1,n]:[!0,""]},isMoney:function(t){var n="请正确填写金额",e=1*t;return!isNaN(e)&&e>0?[!0,""]:[!1,n]}})}).call(n,e(1))},,function(t,n,e){(function(t){"use strict";function e(t){if(Array.isArray(t)){for(var n=0,e=Array(t.length);n<t.length;n++)e[n]=t[n];return e}return Array.from(t)}function r(t,n){if(!(t instanceof n))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(n,"__esModule",{value:!0});var i=function(){function t(t,n){for(var e=0;e<n.length;e++){var r=n[e];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}return function(n,e,r){return e&&t(n.prototype,e),r&&t(n,r),n}}();n.Automatic=function(){function n(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],e=t.submit,i=void 0===e?null:e,a=t.checklist,o=void 0===a?[]:a,s=t.otherlist,u=void 0===s?[]:s,c=t.done,l=void 0===c?null:c;r(this,n);var d=[i,u,o,l];this.submit=d[0],this.otherlist=d[1],this.checklist=d[2],this.callback=d[3],this.allCheck=this.allRequire(),this.canSubmit=this.canSubmit.bind(this),this.isEmptyString=this.isEmptyString.bind(this),this.isEmptyArray=this.isEmptyArray.bind(this),this.check()}return i(n,[{key:"allRequire",value:function(){var t=[].concat(e(this.checklist),e(this.otherlist));return t.filter(function(t){return!!t.required})}},{key:"isEmptyArray",value:function(t){return 0===t.length}},{key:"isEmptyString",value:function(t){return""==t}},{key:"check",value:function(){if(this.isEmptyArray(this.checklist))return console.log("checklist is none");var t=this,n=null;this.checklist.forEach(function(e){var r="select"===e.target.attr("type")?"change":"input";e.target.on(r,function(){t.style(e.target),n=t.canSubmit(),t.callback&&t.callback(n)})})}},{key:"style",value:function(n){var e=this.isEmptyString(n.val()),r=n.attr("data-icon"),i=n.attr("data-other"),a=n.attr("data-operation");e&&(""!=r&&n.siblings("."+r).removeClass("active"),""!=i&&t("."+i).attr("disabled","true"),""!=a&&n.siblings("."+a).hide()),e||(""!=r&&n.siblings("."+r).addClass("active"),""!=i&&t("."+i).removeAttr("disabled"),""!=a&&n.siblings("."+a).show())}},{key:"canSubmit",value:function(){var t="text|tel|password|select|",n=this,e=this.allCheck.every(function(e){var r=e.target;return t.indexOf(r.attr("type"))>=0?!n.isEmptyString(r.val()):t.indexOf(e.target)<0?"checkbox"==r.attr("type")&&r.prop("checked")?!0:0==e.target.length:void 0});return e?this.submit.removeAttr("disabled"):this.submit.attr("disabled","true"),e}},{key:"operationClear",value:function(){t(".wx-clear-input").on("click",function(){t(this).siblings("input").val("").trigger("input")})}},{key:"operationPassword",value:function(){t(".wx-password-operation").on("click",function(){var n=t(this).siblings("input").attr("type");"text"==n&&(t(this).siblings().attr("type","password"),t(this).addClass("wx-hide-password").removeClass("wx-show-password")),"password"==n&&(t(this).siblings().attr("type","text"),t(this).addClass("wx-show-password").removeClass("wx-hide-password"))})}}]),n}()}).call(n,e(1))}]);