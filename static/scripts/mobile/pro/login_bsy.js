webpackJsonp([8],[function(t,n,e){(function(t){"use strict";var n=function(){function t(t,n){var e=[],i=!0,r=!1,o=void 0;try{for(var a,s=t[Symbol.iterator]();!(i=(a=s.next()).done)&&(e.push(a.value),!n||e.length!==n);i=!0);}catch(u){r=!0,o=u}finally{try{!i&&s["return"]&&s["return"]()}finally{if(r)throw o}}return e}return function(n,e){if(Array.isArray(n))return n;if(Symbol.iterator in Object(n))return t(n,e);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),i=e(5),r=e(4),o=e(2),a=e(3);!function(){function e(t){return new Promise(function(n,e){(0,r.ajax)({url:t,type:"POST",data:{identifier:u.val(),password:c.val()},beforeSend:function(){s.text("登录中,请稍等...").attr("disabled","true")},success:function(t){n(t)},error:function(t){e(t)},complete:function(){s.text("登录网利宝").removeAttr("disabled")}})})}var s=t("button[type=submit]"),u=t("input[name=identifier]"),c=t("input[name=password]"),l=[{target:u,required:!0},{target:c,required:!0}],d=new i.Automatic({submit:s,checklist:l});d.operationClear(),d.operationPassword();var f=function(){return new Promise(function(t,e){function i(){var t=[{type:"phone",value:u.val()},{type:"password",value:c.val()}];return(0,a.check)(t)}var r=i(),s=n(r,2),l=s[0],d=s[1];return l?t("验证成功"):((0,o.signModel)(d),console.log("验证失败"))})};s.on("click",function(){f().then(function(t){return console.log(t),e("/weixin/api/login/")}).then(function(t){console.log("login success");var n=(0,r.getQueryStringByName)("next");window.location.href=n?decodeURIComponent(decodeURIComponent(n)):"/weixin/account/"})["catch"](function(t){if(403==t.status)return(0,o.signModel)("请勿重复提交"),!1;var n=JSON.parse(t.responseText);for(var e in n)n.__all__?(0,o.signModel)(n.__all__[0]):(0,o.signModel)(n[e][0])})})}()}).call(n,e(1))},,function(t,n,e){(function(t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});n.Alert=function(n,e){var i=t(".wx-alert"),r=t(".wx-submit");i.css("display","-webkit-box").find(".wx-text").text(n),r.on("click",function(){i.hide(),e()})},n.Confirm=function(n){var e=arguments.length<=1||void 0===arguments[1]?"确定":arguments[1],i=arguments.length<=2||void 0===arguments[2]?null:arguments[2],r=arguments.length<=3||void 0===arguments[3]?null:arguments[3],o=t(".confirm-warp");o.length<=0||(o.show(),o.find(".confirm-text").text(n),o.find(".confirm-certain").text(e),o.find(".confirm-cancel").on("click",function(){o.hide()}),o.find(".confirm-certain").on("click",function(){o.hide(),i&&(r?i(r):i())}))},n.signModel=function(n){t(".error-sign").html(n).removeClass("moveDown").addClass("moveDown").one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",function(){t(this).removeClass("moveDown")})}}).call(n,e(1))},function(t,n,e){(function(t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});var e=function(){function t(t,n){var e=[],i=!0,r=!1,o=void 0;try{for(var a,s=t[Symbol.iterator]();!(i=(a=s.next()).done)&&(e.push(a.value),!n||e.length!==n);i=!0);}catch(u){r=!0,o=u}finally{try{!i&&s["return"]&&s["return"]()}finally{if(r)throw o}}return e}return function(n,e){if(Array.isArray(n))return n;if(Symbol.iterator in Object(n))return t(n,e);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),i=(n.check=function(n){var r=null,o=null;return t.each(n,function(t,n){var a=i[n.type](n.value),s=e(a,2);return r=s[0],o=s[1],r?void 0:!1}),[r,o]},{phone:function r(n){var r=parseInt(t.trim(n)),e="请输入正确的手机号",i=new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);return i.test(r)?[!0,""]:[!1,e]},password:function(n){var e="密码为6-20位数字/字母/符号/区分大小写";new RegExp(/^\d{6,20}$/);return 6<t.trim(n).length&&t.trim(n).length<20?[!0,""]:[!1,e]},rePassword:function(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],n=t.psw,e=void 0===n?null:n,i=t.repeatPsw,r=void 0===i?null:i,o="两次密码不相同";return e!==r?[!1,o]:[!0,""]},tranPassword:function(n){var e="交易密码为6位数字",i=new RegExp(/^\d{6}$/);return i.test(t.trim(n))&&!isNaN(t.trim(n))?[!0,""]:[!1,e]},bankCard:function(n){var e="银行卡号不正确",i=new RegExp(/^\d{12,20}$/);return i.test(t.trim(n))&&!isNaN(t.trim(n))?[!0,""]:[!1,e]},idCard:function(n){var e="身份证号不正确",i=new RegExp(/^([0-9]{17}([0-9]|x|X){1})|([0-9]{15})$/);return i.test(t.trim(n))?[!0,""]:[!1,e]},money100:function(t){var n="请输入100的倍数金额";return t%100===0?[!0,""]:[!1,n]},isEmpty:function(t){var n="请填写全部的表单";return""===t?[!1,n]:[!0,""]},isMoney:function(t){var n="请正确填写金额",e=1*t;return!isNaN(e)&&e>0?[!0,""]:[!1,n]}})}).call(n,e(1))},,function(t,n,e){(function(t){"use strict";function e(t){if(Array.isArray(t)){for(var n=0,e=Array(t.length);n<t.length;n++)e[n]=t[n];return e}return Array.from(t)}function i(t,n){if(!(t instanceof n))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(n,"__esModule",{value:!0});var r=function(){function t(t,n){for(var e=0;e<n.length;e++){var i=n[e];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}return function(n,e,i){return e&&t(n.prototype,e),i&&t(n,i),n}}();n.Automatic=function(){function n(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],e=t.submit,r=void 0===e?null:e,o=t.checklist,a=void 0===o?[]:o,s=t.otherlist,u=void 0===s?[]:s,c=t.done,l=void 0===c?null:c;i(this,n);var d=[r,u,a,l];this.submit=d[0],this.otherlist=d[1],this.checklist=d[2],this.callback=d[3],this.allCheck=this.allRequire(),this.canSubmit=this.canSubmit.bind(this),this.isEmptyString=this.isEmptyString.bind(this),this.isEmptyArray=this.isEmptyArray.bind(this),this.check()}return r(n,[{key:"allRequire",value:function(){var t=[].concat(e(this.checklist),e(this.otherlist));return t.filter(function(t){return!!t.required})}},{key:"isEmptyArray",value:function(t){return 0===t.length}},{key:"isEmptyString",value:function(t){return""==t}},{key:"check",value:function(){if(this.isEmptyArray(this.checklist))return console.log("checklist is none");var t=this,n=null;this.checklist.forEach(function(e){var i="select"===e.target.attr("type")?"change":"input";e.target.on(i,function(){t.style(e.target),n=t.canSubmit(),t.callback&&t.callback(n)})})}},{key:"style",value:function(n){var e=this.isEmptyString(n.val()),i=n.attr("data-icon"),r=n.attr("data-other"),o=n.attr("data-operation");e&&(""!=i&&n.siblings("."+i).removeClass("active"),""!=r&&t("."+r).attr("disabled","true"),""!=o&&n.siblings("."+o).hide()),e||(""!=i&&n.siblings("."+i).addClass("active"),""!=r&&t("."+r).removeAttr("disabled"),""!=o&&n.siblings("."+o).show())}},{key:"canSubmit",value:function(){var t="text|tel|password|select|",n=this,e=this.allCheck.every(function(e){var i=e.target;return t.indexOf(i.attr("type"))>=0?!n.isEmptyString(i.val()):t.indexOf(e.target)<0?"checkbox"==i.attr("type")&&i.prop("checked")?!0:0==e.target.length:void 0});return e?this.submit.removeAttr("disabled"):this.submit.attr("disabled","true"),e}},{key:"operationClear",value:function(){t(".wx-clear-input").on("click",function(){t(this).siblings("input").val("").trigger("input")})}},{key:"operationPassword",value:function(){t(".wx-password-operation").on("click",function(){var n=t(this).siblings("input").attr("type");"text"==n&&(t(this).siblings().attr("type","password"),t(this).addClass("wx-hide-password").removeClass("wx-show-password")),"password"==n&&(t(this).siblings().attr("type","text"),t(this).addClass("wx-show-password").removeClass("wx-hide-password"))})}}]),n}()}).call(n,e(1))}]);