webpackJsonp([1],[function(t,e,n){(function(t){"use strict";var e="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol?"symbol":typeof t},i=function(){function t(t,e){var n=[],i=!0,r=!1,a=void 0;try{for(var o,l=t[Symbol.iterator]();!(i=(o=l.next()).done)&&(n.push(o.value),!e||n.length!==e);i=!0);}catch(s){r=!0,a=s}finally{try{!i&&l["return"]&&l["return"]()}finally{if(r)throw a}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),r=n(2),a=n(3),o=n(5),l=n(4),s=n(12),u=n(10);!function(){function n(n){(0,l.ajax)({type:"POST",url:"/api/pay/cnp/dynnum_new/",data:{phone:v.val(),vcode:h.val(),order_id:t("input[name=order_id]").val(),token:t("input[name=token]").val(),set_the_one_card:!0},beforeSend:function(){n.firstRecharge?c.attr("disabled","disabled").text("充值中..."):c.attr("disabled","disabled").text("绑卡中...")},success:function(i){if(i.ret_code>0)return(0,r.Alert)(i.message);if(t(".error-sign").remove(),n.firstRecharge)t(".sign-main").css("display","-webkit-box").find(".balance-sign").text(i.amount);else{var a=function(){var t=(0,l.getQueryStringByName)("next"),e=""==t?"/weixin/list/":t;return{v:(0,r.Alert)("绑卡成功！",function(){window.location.href=e})}}();if("object"===("undefined"==typeof a?"undefined":e(a)))return a.v}},error:function(t){var e=JSON.parse(t.responseText);return(0,r.Alert)(e.detail)},complete:function(){n.firstRecharge?c.removeAttr("disabled").text("绑卡并充值"):c.removeAttr("disabled").text("立即绑卡")}})}var c=t("button[type=submit]"),d=t("select[name=bank]"),f=t("input[name=bankcard]"),v=t("input[name=bankphone]"),h=t("input[name=validation]"),m=t("input[name=money]"),p=[{target:d,required:!0},{target:f,required:!0},{target:v,required:!0},{target:h,required:!0},{target:m,required:!0}],y=new o.Automatic({submit:c,checklist:p});y.operationClear();var b=[{target:d,required:!0},{target:f,required:!0},{target:v,required:!0}],g=(new o.Automatic({submit:t(".regist-validation"),checklist:b}),function(){return new Promise(function(t,e){function n(){var t=[{type:"isEmpty",value:d.val()},{type:"bankCard",value:f.val()},{type:"phone",value:v.val()},{type:"isEmpty",value:h.val()}];return(0,a.check)(t)}var o=n(),l=i(o,2),s=l[0],u=l[1];return s?t("验证成功"):((0,r.signModel)(u),console.log("验证失败"))})}),k=function(t){var e="";for(var n in t)e+='<option value ="'+t[n].gate_id+'" >'+t[n].name+"</option>";return e},_=function(t){if(localStorage.getItem("bank_update")){var e=JSON.parse(localStorage.getItem("bank_update"));return d.append(k(e)),t&&t(e)}(0,l.ajax)({type:"POST",url:"/api/bank/list_new/",success:function(e){if(0===e.ret_code){var n=JSON.stringify(e.banks);return d.append(k(e.banks)),window.localStorage.setItem("bank_update",n),t&&t(e.banks)}return(0,r.Alert)(e.message)},error:function(t){console.log(t)}})};_(function(e){u.limit.getInstance({target:t(".limit-bank-item"),limit_data:e})});var w=t("button[name=validation_btn]"),x=new s.Simple_validation({target:w,VALIDATION_URL:"/api/pay/deposit_new/"});w.on("click",function(){x.set_check_list([{type:"isEmpty",value:d.val()},{type:"bankCard",value:f.val()},{type:"phone",value:v.val()}]),x.set_ajax_data({card_no:f.val(),gate_id:d.val(),phone:v.val(),amount:m.length>0?m.val():.01}),x.start()}),c.on("click",function(){var e=this;g().then(function(i){var a=t(e).attr("data-recharge");"true"==a?(0,r.Confirm)("充值金额为"+m.val(),"确认充值",n,{firstRecharge:!0}):n({firstRecharge:!1})})["catch"](function(t){})})}()}).call(e,n(1))},,function(t,e,n){(function(t){"use strict";Object.defineProperty(e,"__esModule",{value:!0});e.Alert=function(e,n){var i=t(".wx-alert"),r=t(".wx-submit");i.css("display","-webkit-box").find(".wx-text").text(e),r.on("click",function(){i.hide(),n&&n()})},e.Confirm=function(e){var n=arguments.length<=1||void 0===arguments[1]?"确定":arguments[1],i=arguments.length<=2||void 0===arguments[2]?null:arguments[2],r=arguments.length<=3||void 0===arguments[3]?null:arguments[3],a=t(".confirm-warp");a.length<=0||(a.show(),a.find(".confirm-text").text(e),a.find(".confirm-certain").text(n),a.find(".confirm-cancel").on("click",function(){a.hide()}),a.find(".confirm-certain").on("click",function(){a.hide(),i&&(r?i(r):i())}))},e.signModel=function(e){t(".error-sign").html(e).removeClass("moveDown").addClass("moveDown").one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",function(){t(this).removeClass("moveDown")})}}).call(e,n(1))},function(t,e,n){(function(t){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=function(){function t(t,e){var n=[],i=!0,r=!1,a=void 0;try{for(var o,l=t[Symbol.iterator]();!(i=(o=l.next()).done)&&(n.push(o.value),!e||n.length!==e);i=!0);}catch(s){r=!0,a=s}finally{try{!i&&l["return"]&&l["return"]()}finally{if(r)throw a}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),i=(e.check=function(e){var r=null,a=null;return t.each(e,function(t,e){var o=i[e.type](e.value),l=n(o,2);return r=l[0],a=l[1],r?void 0:!1}),[r,a]},{phone:function r(e){var r=parseInt(t.trim(e)),n="请输入正确的手机号",i=new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0123456789])[0-9]{8}$/);return i.test(r)?[!0,""]:[!1,n]},password:function(e){var n="密码为6-20位数字/字母/符号/区分大小写";return 6<=t.trim(e).length&&t.trim(e).length<=20?[!0,""]:[!1,n]},rePassword:function(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],e=t.psw,n=void 0===e?null:e,i=t.repeatPsw,r=void 0===i?null:i,a="两次密码不相同";return n!==r?[!1,a]:[!0,""]},tranPassword:function(e){var n="交易密码为6位数字",i=new RegExp(/^\d{6}$/);return i.test(t.trim(e))&&!isNaN(t.trim(e))?[!0,""]:[!1,n]},bankCard:function(e){var n="银行卡号不正确",i=new RegExp(/^\d{12,20}$/);return i.test(t.trim(e))&&!isNaN(t.trim(e))?[!0,""]:[!1,n]},idCard:function(e){var n="身份证号不正确",i=new RegExp(/^([0-9]{17}([0-9]|x|X){1})|([0-9]{15})$/);return i.test(t.trim(e))?[!0,""]:[!1,n]},money100:function(t){var e="请输入100的倍数金额";return t%100===0?[!0,""]:[!1,e]},isEmpty:function(t){var e="请填写全部的表单";return""===t?[!1,e]:[!0,""]},isMoney:function(t){var e="请正确填写金额",n=1*t;return!isNaN(n)&&n>0?[!0,""]:[!1,e]}})}).call(e,n(1))},,function(t,e,n){(function(t){"use strict";function n(t){if(Array.isArray(t)){for(var e=0,n=Array(t.length);e<t.length;e++)n[e]=t[e];return n}return Array.from(t)}function i(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(e,"__esModule",{value:!0});var r=function(){function t(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}return function(e,n,i){return n&&t(e.prototype,n),i&&t(e,i),e}}();e.Automatic=function(){function e(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],n=t.submit,r=void 0===n?null:n,a=t.checklist,o=void 0===a?[]:a,l=t.otherlist,s=void 0===l?[]:l,u=t.done,c=void 0===u?null:u;i(this,e);var d=[r,s,o,c];this.submit=d[0],this.otherlist=d[1],this.checklist=d[2],this.callback=d[3],this.allCheck=this.allRequire(),this.canSubmit=this.canSubmit.bind(this),this.isEmptyString=this.isEmptyString.bind(this),this.isEmptyArray=this.isEmptyArray.bind(this),this.check()}return r(e,[{key:"allRequire",value:function(){var t=[].concat(n(this.checklist),n(this.otherlist));return t.filter(function(t){return!!t.required})}},{key:"isEmptyArray",value:function(t){return 0===t.length}},{key:"isEmptyString",value:function(t){return""==t}},{key:"check",value:function(){if(this.isEmptyArray(this.checklist))return console.log("checklist is none");var t=this,e=null;this.checklist.forEach(function(n){var i="select"===n.target.attr("type")?"change":"input";n.target.on(i,function(){t.style(n.target),e=t.canSubmit(),t.callback&&t.callback(e)})})}},{key:"style",value:function(e){var n=this.isEmptyString(e.val()),i=e.attr("data-icon"),r=e.attr("data-other"),a=e.attr("data-operation");n&&(""!=i&&e.siblings("."+i).removeClass("active"),""!=r&&t("."+r).attr("disabled","true"),""!=a&&e.siblings("."+a).hide()),n||(""!=i&&e.siblings("."+i).addClass("active"),""!=r&&t("."+r).removeAttr("disabled"),""!=a&&e.siblings("."+a).show())}},{key:"canSubmit",value:function(){var t="text|tel|password|select|",e=this,n=this.allCheck.every(function(n){var i=n.target;return t.indexOf(i.attr("type"))>=0?!e.isEmptyString(i.val()):t.indexOf(n.target)<0?"checkbox"==i.attr("type")&&i.prop("checked")?!0:0==n.target.length:void 0});return n?this.submit.removeAttr("disabled"):this.submit.attr("disabled","true"),n}},{key:"operationClear",value:function(){t(".wx-clear-input").on("click",function(){t(this).siblings("input").val("").trigger("input")})}},{key:"operationPassword",value:function(){t(".wx-password-operation").on("click",function(){var e=t(this).siblings("input").attr("type");"text"==e&&(t(this).siblings().attr("type","password"),t(this).addClass("wx-hide-password").removeClass("wx-show-password")),"password"==e&&(t(this).siblings().attr("type","text"),t(this).addClass("wx-show-password").removeClass("wx-hide-password"))})}}]),e}()}).call(e,n(1))},,,,,function(t,e){"use strict";function n(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(e,"__esModule",{value:!0});var i=function(){function t(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}return function(e,n,i){return n&&t(e.prototype,n),i&&t(e,i),e}}();e.limit=function(){var t=null,e=function(){function t(){var e=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],i=e.target,r=void 0===i?null:i,a=e.limit_data,o=void 0===a?null:a;n(this,t);var l=[r,o];this.target=l[0],this.limit_data=l[1],this._format_limit=this._format_limit.bind(this),this.target.html(this._style(this.limit_data))}return i(t,[{key:"_style",value:function(t){for(var e="",n=0;n<t.length;n++)e+="<div class='limit-bank-list'>",e+="<div class='limit-list-dec'>",e+="<div class='bank-name'>"+t[n].name+"</div>",e+="<div class='bank-limit'>首次限额"+this._format_limit(t[n].first_one)+"/单笔限额"+this._format_limit(t[n].first_one)+"/日限额"+this._format_limit(t[n].second_day)+"</div>",e+="</div>",e+="<div class='limit-list-icon "+t[n].bank_id+"'></div>",e+="</div>";return e}},{key:"_format_limit",value:function(t){var e=t,n=/^\d{5,}$/,i=/^\d{4}$/;return n.test(t)?e=t.replace("0000","")+"万":i.test(t)?e=t.replace("000","")+"千":void 0}}]),t}(),r=function(n){return t||(t=new e(n)),t};return{getInstance:r}}()},,function(t,e,n){(function(t){"use strict";function i(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(e,"__esModule",{value:!0}),e.Simple_validation=void 0;var r=function(){function t(t,e){var n=[],i=!0,r=!1,a=void 0;try{for(var o,l=t[Symbol.iterator]();!(i=(o=l.next()).done)&&(n.push(o.value),!e||n.length!==e);i=!0);}catch(s){r=!0,a=s}finally{try{!i&&l["return"]&&l["return"]()}finally{if(r)throw a}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),a=function(){function t(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}return function(e,n,i){return n&&t(e.prototype,n),i&&t(e,i),e}}(),o=n(4),l=n(2),s=n(3);e.Simple_validation=function(){function e(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],n=t.target,r=void 0===n?null:n,a=t.VALIDATION_URL,o=void 0===a?null:a,l=t.callback,s=void 0===l?null:l;i(this,e);var u=[r,o,s];this.target=u[0],this.VALIDATION_URL=u[1],this.callback=u[2],this.post_data=null,this.check_list=null,this.intervalId=null,this.before_validation=this.before_validation.bind(this),this.timerFunction=this.timerFunction.bind(this),this.execute_request=this.execute_request.bind(this)}return a(e,[{key:"set_ajax_data",value:function(t){this.post_data=t}},{key:"set_check_list",value:function(t){this.check_list=t}},{key:"before_validation",value:function(){var t=this.check_list;return new Promise(function(e,n){function i(){var e=t;return(0,s.check)(e)}var a=i(),o=r(a,2),l=o[0],u=o[1];return l?e("验证成功"):n(u)})}},{key:"execute_request",value:function(){var e=this.target,n=this.VALIDATION_URL,i=this.post_data,r=this.intervalId;return new Promise(function(a,l){(0,o.ajax)({url:n,type:"POST",data:i,beforeSend:function(){e.attr("disabled","disabled").text("发送中..")},success:function(n){return n.ret_code>0?(clearInterval(r),e.text("重新获取").removeAttr("disabled").css("background","#50b143"),l(n.message)):(t("input[name='order_id']").val(n.order_id),t("input[name='token']").val(n.token),a("短信已发送，请注意查收！"))},error:function(t){return clearInterval(r),e.text("重新获取").removeAttr("disabled").css("background","#50b143"),l(t)}})})}},{key:"timerFunction",value:function(t){var e=this.target,n=void 0,i=function(){return t>1?(t--,e.text(t+"秒后可重发")):(clearInterval(n),e.text("重新获取").removeAttr("disabled"),(0,l.signModel)("倒计时失效，请重新获取"))};return i(),n=setInterval(i,1e3),this.intervalId=n}},{key:"start",value:function(){var t=this;this.before_validation().then(function(e){return console.log("验证通过"),t.execute_request()}).then(function(e){(0,l.signModel)(e),t.timerFunction(60)})["catch"](function(t){return(0,l.signModel)(t)})}}]),e}()}).call(e,n(1))}]);