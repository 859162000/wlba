webpackJsonp([4],[function(t,e,n){(function(t){"use strict";var e=function(){function t(t,e){var n=[],r=!0,i=!1,o=void 0;try{for(var a,u=t[Symbol.iterator]();!(r=(a=u.next()).done)&&(n.push(a.value),!e||n.length!==e);r=!0);}catch(s){i=!0,o=s}finally{try{!r&&u["return"]&&u["return"]()}finally{if(i)throw o}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),r=n(3),i=n(5),o=n(2),a=n(4);!function(){function n(t){return new Promise(function(e,n){(0,o.ajax)({url:t,type:"POST",data:{name:s.val(),id_number:c.val()},beforeSend:function(){u.text("认证中,请稍等...").attr("disabled","true")},success:function(t){e(t)},error:function(t){n(t)},complete:function(){u.text("实名认证").removeAttr("disabled")}})})}var u=t("button[type=submit]"),s=t("input[name=username]"),c=t("input[name=idcard]"),l=[{target:s,required:!0},{target:c,required:!0}],f=new i.Automatic({submit:u,checklist:l});f.operation();var d=function(){return new Promise(function(t,n){function i(){var t=[{type:"isEmpty",value:s.val()},{type:"idCard",value:c.val()}];return(0,a.check)(t)}var o=i(),u=e(o,2),l=u[0],f=u[1];return l?t("验证成功"):((0,r.ui_signError)(f),console.log("验证失败"))})};u.on("click",function(){d().then(function(t){return console.log(t),n("/api/id_validate/")}).then(function(t){(0,r.ui_alert)("实名认证成功",function(){window.location.href="/fuel_card/regist/bank/"})})["catch"](function(t){return result=JSON.parse(t.responseText),(0,r.ui_signError)(result.message)})})}()}).call(e,n(1))},,function(t,e,n){(function(t){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=(e.ajax=function(e){t.ajax({url:e.url,type:e.type,data:e.data,dataType:e.dataType,async:e.async||!0,beforeSend:function(t,o){e.beforeSend&&e.beforeSend(t),!r(o.type)&&i(o.url)&&t.setRequestHeader("X-CSRFToken",n("csrftoken"))},success:function(t){e.success&&e.success(t)},error:function(t){e.error&&e.error(t)},complete:function(){e.complete&&e.complete()}})},e.getCookie=function(e){var n=void 0,r=void 0,i=void 0,o=null;if(document.cookie&&""!==document.cookie)for(r=document.cookie.split(";"),i=0;i<r.length;){if(n=t.trim(r[i]),n.substring(0,e.length+1)===e+"="){o=decodeURIComponent(n.substring(e.length+1));break}i++}return o}),r=function(t){return/^(GET|HEAD|OPTIONS|TRACE)$/.test(t)},i=function(t){var e=void 0,n=void 0,r=void 0,i=void 0;return e=document.location.host,r=document.location.protocol,i="//"+e,n=r+i,t===n||t.slice(0,n.length+1)===n+"/"||t===i||t.slice(0,i.length+1)===i+"/"||!/^(\/\/|http:|https:).*/.test(t)}}).call(e,n(1))},function(t,e,n){(function(t){"use strict";Object.defineProperty(e,"__esModule",{value:!0});e.ui_alert=function(e,n){var r=t(".fuel-alert"),i=t(".fuel-submit");r.css("display","-webkit-box").find(".fuel-text").text(e),i.on("click",function(){r.hide(),n&&n()})},e.ui_confirm=function(e){var n=arguments.length<=1||void 0===arguments[1]?"确定":arguments[1],r=arguments.length<=2||void 0===arguments[2]?null:arguments[2],i=arguments.length<=3||void 0===arguments[3]?null:arguments[3],o=t(".confirm-warp");o.length<=0||(o.show(),o.find(".confirm-text").text(e),o.find(".confirm-certain").text(n),o.find(".confirm-cancel").on("click",function(){o.hide()}),o.find(".confirm-certain").on("click",function(){o.hide(),r&&(i?r(i):r())}))},e.ui_signError=function(e){t(".error-sign").html(e).removeClass("moveDown").addClass("moveDown").one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",function(){t(this).removeClass("moveDown")})}}).call(e,n(1))},function(t,e,n){(function(t){"use strict";var n=function(){function t(t,e){var n=[],r=!0,i=!1,o=void 0;try{for(var a,u=t[Symbol.iterator]();!(r=(a=u.next()).done)&&(n.push(a.value),!e||n.length!==e);r=!0);}catch(s){i=!0,o=s}finally{try{!r&&u["return"]&&u["return"]()}finally{if(i)throw o}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}();Object.defineProperty(e,"__esModule",{value:!0});var r=(e.check=function(e){var i=null,o=null;return t.each(e,function(t,e){var a=r[e.type](e.value),u=n(a,2);return i=u[0],o=u[1],i?void 0:!1}),[i,o]},{phone:function i(e){var i=parseInt(t.trim(e)),n="请输入正确的手机号",r=new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);return r.test(i)?[!0,""]:[!1,n]},password:function(e){var n="密码为6-20位数字/字母/符号/区分大小写",r=new RegExp(/^\d{6,20}$/);return r.test(t.trim(e))?[!0,""]:[!1,n]},rePassword:function(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],e=t.psw,n=void 0===e?null:e,r=t.repeatPsw,i=void 0===r?null:r,o="两次密码不相同";return n!==i?[!1,o]:[!0,""]},tranPassword:function(e){var n="交易密码为6位数字",r=new RegExp(/^\d{6}$/);return r.test(t.trim(e))&&!isNaN(t.trim(e))?[!0,""]:[!1,n]},bankCard:function(e){var n="银行卡号不正确",r=new RegExp(/^\d{12,20}$/);return r.test(t.trim(e))&&!isNaN(t.trim(e))?[!0,""]:[!1,n]},idCard:function(e){var n="身份证号不正确",r=new RegExp(/^.{15,18}$/);return r.test(t.trim(e))&&!isNaN(t.trim(e))?[!0,""]:[!1,n]},money100:function(t){var e="请输入100的倍数金额";return t%100===0?[!0,""]:[!1,e]},isEmpty:function(t){var e="请填写全部的表单";return""===t?[!1,e]:[!0,""]}})}).call(e,n(1))},function(t,e,n){(function(t){"use strict";function n(t){if(Array.isArray(t)){for(var e=0,n=Array(t.length);e<t.length;e++)n[e]=t[e];return n}return Array.from(t)}function r(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}var i=function(){function t(t,e){for(var n=0;n<e.length;n++){var r=e[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,r.key,r)}}return function(e,n,r){return n&&t(e.prototype,n),r&&t(e,r),e}}();Object.defineProperty(e,"__esModule",{value:!0});e.Automatic=function(){function e(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],n=t.submit,i=void 0===n?null:n,o=t.checklist,a=void 0===o?[]:o,u=t.otherlist,s=void 0===u?[]:u;r(this,e);var c=[i,s,a];this.submit=c[0],this.otherlist=c[1],this.checklist=c[2],this.allCheck=this.allRequire(),this.canSubmit=this.canSubmit.bind(this),this.isEmptyString=this.isEmptyString.bind(this),this.isEmptyArray=this.isEmptyArray.bind(this),this.check()}return i(e,[{key:"allRequire",value:function(){var t=[].concat(n(this.checklist),n(this.otherlist));return t.filter(function(t){return t.required?!0:!1})}},{key:"isEmptyArray",value:function(t){return 0===t.length?!0:!1}},{key:"isEmptyString",value:function(t){return""==t?!0:!1}},{key:"check",value:function(){if(this.isEmptyArray(this.checklist))return console.log("checklist is none");var t=this;this.checklist.forEach(function(e){e.target.on("input",function(){t.style(e.target),t.canSubmit()})})}},{key:"style",value:function(e){var n=this.isEmptyString(e.val()),r=e.attr("data-icon"),i=e.attr("data-other"),o=e.attr("data-operation");n&&(""!=r&&e.siblings("."+r).removeClass("active"),""!=i&&t("."+i).attr("disabled","true"),""!=o&&e.siblings("."+o).hide()),n||(""!=r&&e.siblings("."+r).addClass("active"),""!=i&&t("."+i).removeAttr("disabled"),""!=o&&e.siblings("."+o).show())}},{key:"canSubmit",value:function(){var t="text|tel|password|select|",e=this,n=this.allCheck.every(function(n){var r=n.target;return t.indexOf(r.attr("type"))>=0?e.isEmptyString(r.val())?!1:!0:t.indexOf(n.target)<0?"checkbox"==r.attr("type")&&r.prop("checked")?!0:!1:void 0});n?this.submit.removeAttr("disabled"):this.submit.attr("disabled","true")}},{key:"operation",value:function(){t(".fuel-clear-input").on("click",function(){t(this).siblings("input").val("").trigger("input")})}},{key:"operationPassword",value:function(){t(".fuel-password-operation").on("click",function(){var e=t(this).siblings("input").attr("type");"text"==e&&(t(this).siblings().attr("type","password"),t(this).addClass("fuel-hide-password").removeClass("fuel-show-password")),"password"==e&&(t(this).siblings().attr("type","text"),t(this).addClass("fuel-show-password").removeClass("fuel-hide-password"))})}}]),e}()}).call(e,n(1))}]);