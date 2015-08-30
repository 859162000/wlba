/* Zepto v1.1.6 - zepto event ajax form ie - zeptojs.com/license */
var Zepto=function(){function L(t){return null==t?String(t):j[S.call(t)]||"object"}function Z(t){return"function"==L(t)}function _(t){return null!=t&&t==t.window}function $(t){return null!=t&&t.nodeType==t.DOCUMENT_NODE}function D(t){return"object"==L(t)}function M(t){return D(t)&&!_(t)&&Object.getPrototypeOf(t)==Object.prototype}function R(t){return"number"==typeof t.length}function k(t){return s.call(t,function(t){return null!=t})}function z(t){return t.length>0?n.fn.concat.apply([],t):t}function F(t){return t.replace(/::/g,"/").replace(/([A-Z]+)([A-Z][a-z])/g,"$1_$2").replace(/([a-z\d])([A-Z])/g,"$1_$2").replace(/_/g,"-").toLowerCase()}function q(t){return t in f?f[t]:f[t]=new RegExp("(^|\\s)"+t+"(\\s|$)")}function H(t,e){return"number"!=typeof e||c[F(t)]?e:e+"px"}function I(t){var e,n;return u[t]||(e=a.createElement(t),a.body.appendChild(e),n=getComputedStyle(e,"").getPropertyValue("display"),e.parentNode.removeChild(e),"none"==n&&(n="block"),u[t]=n),u[t]}function V(t){return"children"in t?o.call(t.children):n.map(t.childNodes,function(t){return 1==t.nodeType?t:void 0})}function B(n,i,r){for(e in i)r&&(M(i[e])||A(i[e]))?(M(i[e])&&!M(n[e])&&(n[e]={}),A(i[e])&&!A(n[e])&&(n[e]=[]),B(n[e],i[e],r)):i[e]!==t&&(n[e]=i[e])}function U(t,e){return null==e?n(t):n(t).filter(e)}function J(t,e,n,i){return Z(e)?e.call(t,n,i):e}function X(t,e,n){null==n?t.removeAttribute(e):t.setAttribute(e,n)}function W(e,n){var i=e.className||"",r=i&&i.baseVal!==t;return n===t?r?i.baseVal:i:void(r?i.baseVal=n:e.className=n)}function Y(t){try{return t?"true"==t||("false"==t?!1:"null"==t?null:+t+""==t?+t:/^[\[\{]/.test(t)?n.parseJSON(t):t):t}catch(e){return t}}function G(t,e){e(t);for(var n=0,i=t.childNodes.length;i>n;n++)G(t.childNodes[n],e)}var t,e,n,i,C,N,r=[],o=r.slice,s=r.filter,a=window.document,u={},f={},c={"column-count":1,columns:1,"font-weight":1,"line-height":1,opacity:1,"z-index":1,zoom:1},l=/^\s*<(\w+|!)[^>]*>/,h=/^<(\w+)\s*\/?>(?:<\/\1>|)$/,p=/<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/gi,d=/^(?:body|html)$/i,m=/([A-Z])/g,g=["val","css","html","text","data","width","height","offset"],v=["after","prepend","before","append"],y=a.createElement("table"),x=a.createElement("tr"),b={tr:a.createElement("tbody"),tbody:y,thead:y,tfoot:y,td:x,th:x,"*":a.createElement("div")},w=/complete|loaded|interactive/,E=/^[\w-]*$/,j={},S=j.toString,T={},O=a.createElement("div"),P={tabindex:"tabIndex",readonly:"readOnly","for":"htmlFor","class":"className",maxlength:"maxLength",cellspacing:"cellSpacing",cellpadding:"cellPadding",rowspan:"rowSpan",colspan:"colSpan",usemap:"useMap",frameborder:"frameBorder",contenteditable:"contentEditable"},A=Array.isArray||function(t){return t instanceof Array};return T.matches=function(t,e){if(!e||!t||1!==t.nodeType)return!1;var n=t.webkitMatchesSelector||t.mozMatchesSelector||t.oMatchesSelector||t.matchesSelector;if(n)return n.call(t,e);var i,r=t.parentNode,o=!r;return o&&(r=O).appendChild(t),i=~T.qsa(r,e).indexOf(t),o&&O.removeChild(t),i},C=function(t){return t.replace(/-+(.)?/g,function(t,e){return e?e.toUpperCase():""})},N=function(t){return s.call(t,function(e,n){return t.indexOf(e)==n})},T.fragment=function(e,i,r){var s,u,f;return h.test(e)&&(s=n(a.createElement(RegExp.$1))),s||(e.replace&&(e=e.replace(p,"<$1></$2>")),i===t&&(i=l.test(e)&&RegExp.$1),i in b||(i="*"),f=b[i],f.innerHTML=""+e,s=n.each(o.call(f.childNodes),function(){f.removeChild(this)})),M(r)&&(u=n(s),n.each(r,function(t,e){g.indexOf(t)>-1?u[t](e):u.attr(t,e)})),s},T.Z=function(t,e){return t=t||[],t.__proto__=n.fn,t.selector=e||"",t},T.isZ=function(t){return t instanceof T.Z},T.init=function(e,i){var r;if(!e)return T.Z();if("string"==typeof e)if(e=e.trim(),"<"==e[0]&&l.test(e))r=T.fragment(e,RegExp.$1,i),e=null;else{if(i!==t)return n(i).find(e);r=T.qsa(a,e)}else{if(Z(e))return n(a).ready(e);if(T.isZ(e))return e;if(A(e))r=k(e);else if(D(e))r=[e],e=null;else if(l.test(e))r=T.fragment(e.trim(),RegExp.$1,i),e=null;else{if(i!==t)return n(i).find(e);r=T.qsa(a,e)}}return T.Z(r,e)},n=function(t,e){return T.init(t,e)},n.extend=function(t){var e,n=o.call(arguments,1);return"boolean"==typeof t&&(e=t,t=n.shift()),n.forEach(function(n){B(t,n,e)}),t},T.qsa=function(t,e){var n,i="#"==e[0],r=!i&&"."==e[0],s=i||r?e.slice(1):e,a=E.test(s);return $(t)&&a&&i?(n=t.getElementById(s))?[n]:[]:1!==t.nodeType&&9!==t.nodeType?[]:o.call(a&&!i?r?t.getElementsByClassName(s):t.getElementsByTagName(e):t.querySelectorAll(e))},n.contains=a.documentElement.contains?function(t,e){return t!==e&&t.contains(e)}:function(t,e){for(;e&&(e=e.parentNode);)if(e===t)return!0;return!1},n.type=L,n.isFunction=Z,n.isWindow=_,n.isArray=A,n.isPlainObject=M,n.isEmptyObject=function(t){var e;for(e in t)return!1;return!0},n.inArray=function(t,e,n){return r.indexOf.call(e,t,n)},n.camelCase=C,n.trim=function(t){return null==t?"":String.prototype.trim.call(t)},n.uuid=0,n.support={},n.expr={},n.map=function(t,e){var n,r,o,i=[];if(R(t))for(r=0;r<t.length;r++)n=e(t[r],r),null!=n&&i.push(n);else for(o in t)n=e(t[o],o),null!=n&&i.push(n);return z(i)},n.each=function(t,e){var n,i;if(R(t)){for(n=0;n<t.length;n++)if(e.call(t[n],n,t[n])===!1)return t}else for(i in t)if(e.call(t[i],i,t[i])===!1)return t;return t},n.grep=function(t,e){return s.call(t,e)},window.JSON&&(n.parseJSON=JSON.parse),n.each("Boolean Number String Function Array Date RegExp Object Error".split(" "),function(t,e){j["[object "+e+"]"]=e.toLowerCase()}),n.fn={forEach:r.forEach,reduce:r.reduce,push:r.push,sort:r.sort,indexOf:r.indexOf,concat:r.concat,map:function(t){return n(n.map(this,function(e,n){return t.call(e,n,e)}))},slice:function(){return n(o.apply(this,arguments))},ready:function(t){return w.test(a.readyState)&&a.body?t(n):a.addEventListener("DOMContentLoaded",function(){t(n)},!1),this},get:function(e){return e===t?o.call(this):this[e>=0?e:e+this.length]},toArray:function(){return this.get()},size:function(){return this.length},remove:function(){return this.each(function(){null!=this.parentNode&&this.parentNode.removeChild(this)})},each:function(t){return r.every.call(this,function(e,n){return t.call(e,n,e)!==!1}),this},filter:function(t){return Z(t)?this.not(this.not(t)):n(s.call(this,function(e){return T.matches(e,t)}))},add:function(t,e){return n(N(this.concat(n(t,e))))},is:function(t){return this.length>0&&T.matches(this[0],t)},not:function(e){var i=[];if(Z(e)&&e.call!==t)this.each(function(t){e.call(this,t)||i.push(this)});else{var r="string"==typeof e?this.filter(e):R(e)&&Z(e.item)?o.call(e):n(e);this.forEach(function(t){r.indexOf(t)<0&&i.push(t)})}return n(i)},has:function(t){return this.filter(function(){return D(t)?n.contains(this,t):n(this).find(t).size()})},eq:function(t){return-1===t?this.slice(t):this.slice(t,+t+1)},first:function(){var t=this[0];return t&&!D(t)?t:n(t)},last:function(){var t=this[this.length-1];return t&&!D(t)?t:n(t)},find:function(t){var e,i=this;return e=t?"object"==typeof t?n(t).filter(function(){var t=this;return r.some.call(i,function(e){return n.contains(e,t)})}):1==this.length?n(T.qsa(this[0],t)):this.map(function(){return T.qsa(this,t)}):n()},closest:function(t,e){var i=this[0],r=!1;for("object"==typeof t&&(r=n(t));i&&!(r?r.indexOf(i)>=0:T.matches(i,t));)i=i!==e&&!$(i)&&i.parentNode;return n(i)},parents:function(t){for(var e=[],i=this;i.length>0;)i=n.map(i,function(t){return(t=t.parentNode)&&!$(t)&&e.indexOf(t)<0?(e.push(t),t):void 0});return U(e,t)},parent:function(t){return U(N(this.pluck("parentNode")),t)},children:function(t){return U(this.map(function(){return V(this)}),t)},contents:function(){return this.map(function(){return o.call(this.childNodes)})},siblings:function(t){return U(this.map(function(t,e){return s.call(V(e.parentNode),function(t){return t!==e})}),t)},empty:function(){return this.each(function(){this.innerHTML=""})},pluck:function(t){return n.map(this,function(e){return e[t]})},show:function(){return this.each(function(){"none"==this.style.display&&(this.style.display=""),"none"==getComputedStyle(this,"").getPropertyValue("display")&&(this.style.display=I(this.nodeName))})},replaceWith:function(t){return this.before(t).remove()},wrap:function(t){var e=Z(t);if(this[0]&&!e)var i=n(t).get(0),r=i.parentNode||this.length>1;return this.each(function(o){n(this).wrapAll(e?t.call(this,o):r?i.cloneNode(!0):i)})},wrapAll:function(t){if(this[0]){n(this[0]).before(t=n(t));for(var e;(e=t.children()).length;)t=e.first();n(t).append(this)}return this},wrapInner:function(t){var e=Z(t);return this.each(function(i){var r=n(this),o=r.contents(),s=e?t.call(this,i):t;o.length?o.wrapAll(s):r.append(s)})},unwrap:function(){return this.parent().each(function(){n(this).replaceWith(n(this).children())}),this},clone:function(){return this.map(function(){return this.cloneNode(!0)})},hide:function(){return this.css("display","none")},toggle:function(e){return this.each(function(){var i=n(this);(e===t?"none"==i.css("display"):e)?i.show():i.hide()})},prev:function(t){return n(this.pluck("previousElementSibling")).filter(t||"*")},next:function(t){return n(this.pluck("nextElementSibling")).filter(t||"*")},html:function(t){return 0 in arguments?this.each(function(e){var i=this.innerHTML;n(this).empty().append(J(this,t,e,i))}):0 in this?this[0].innerHTML:null},text:function(t){return 0 in arguments?this.each(function(e){var n=J(this,t,e,this.textContent);this.textContent=null==n?"":""+n}):0 in this?this[0].textContent:null},attr:function(n,i){var r;return"string"!=typeof n||1 in arguments?this.each(function(t){if(1===this.nodeType)if(D(n))for(e in n)X(this,e,n[e]);else X(this,n,J(this,i,t,this.getAttribute(n)))}):this.length&&1===this[0].nodeType?!(r=this[0].getAttribute(n))&&n in this[0]?this[0][n]:r:t},removeAttr:function(t){return this.each(function(){1===this.nodeType&&t.split(" ").forEach(function(t){X(this,t)},this)})},prop:function(t,e){return t=P[t]||t,1 in arguments?this.each(function(n){this[t]=J(this,e,n,this[t])}):this[0]&&this[0][t]},data:function(e,n){var i="data-"+e.replace(m,"-$1").toLowerCase(),r=1 in arguments?this.attr(i,n):this.attr(i);return null!==r?Y(r):t},val:function(t){return 0 in arguments?this.each(function(e){this.value=J(this,t,e,this.value)}):this[0]&&(this[0].multiple?n(this[0]).find("option").filter(function(){return this.selected}).pluck("value"):this[0].value)},offset:function(t){if(t)return this.each(function(e){var i=n(this),r=J(this,t,e,i.offset()),o=i.offsetParent().offset(),s={top:r.top-o.top,left:r.left-o.left};"static"==i.css("position")&&(s.position="relative"),i.css(s)});if(!this.length)return null;var e=this[0].getBoundingClientRect();return{left:e.left+window.pageXOffset,top:e.top+window.pageYOffset,width:Math.round(e.width),height:Math.round(e.height)}},css:function(t,i){if(arguments.length<2){var r,o=this[0];if(!o)return;if(r=getComputedStyle(o,""),"string"==typeof t)return o.style[C(t)]||r.getPropertyValue(t);if(A(t)){var s={};return n.each(t,function(t,e){s[e]=o.style[C(e)]||r.getPropertyValue(e)}),s}}var a="";if("string"==L(t))i||0===i?a=F(t)+":"+H(t,i):this.each(function(){this.style.removeProperty(F(t))});else for(e in t)t[e]||0===t[e]?a+=F(e)+":"+H(e,t[e])+";":this.each(function(){this.style.removeProperty(F(e))});return this.each(function(){this.style.cssText+=";"+a})},index:function(t){return t?this.indexOf(n(t)[0]):this.parent().children().indexOf(this[0])},hasClass:function(t){return t?r.some.call(this,function(t){return this.test(W(t))},q(t)):!1},addClass:function(t){return t?this.each(function(e){if("className"in this){i=[];var r=W(this),o=J(this,t,e,r);o.split(/\s+/g).forEach(function(t){n(this).hasClass(t)||i.push(t)},this),i.length&&W(this,r+(r?" ":"")+i.join(" "))}}):this},removeClass:function(e){return this.each(function(n){if("className"in this){if(e===t)return W(this,"");i=W(this),J(this,e,n,i).split(/\s+/g).forEach(function(t){i=i.replace(q(t)," ")}),W(this,i.trim())}})},toggleClass:function(e,i){return e?this.each(function(r){var o=n(this),s=J(this,e,r,W(this));s.split(/\s+/g).forEach(function(e){(i===t?!o.hasClass(e):i)?o.addClass(e):o.removeClass(e)})}):this},scrollTop:function(e){if(this.length){var n="scrollTop"in this[0];return e===t?n?this[0].scrollTop:this[0].pageYOffset:this.each(n?function(){this.scrollTop=e}:function(){this.scrollTo(this.scrollX,e)})}},scrollLeft:function(e){if(this.length){var n="scrollLeft"in this[0];return e===t?n?this[0].scrollLeft:this[0].pageXOffset:this.each(n?function(){this.scrollLeft=e}:function(){this.scrollTo(e,this.scrollY)})}},position:function(){if(this.length){var t=this[0],e=this.offsetParent(),i=this.offset(),r=d.test(e[0].nodeName)?{top:0,left:0}:e.offset();return i.top-=parseFloat(n(t).css("margin-top"))||0,i.left-=parseFloat(n(t).css("margin-left"))||0,r.top+=parseFloat(n(e[0]).css("border-top-width"))||0,r.left+=parseFloat(n(e[0]).css("border-left-width"))||0,{top:i.top-r.top,left:i.left-r.left}}},offsetParent:function(){return this.map(function(){for(var t=this.offsetParent||a.body;t&&!d.test(t.nodeName)&&"static"==n(t).css("position");)t=t.offsetParent;return t})}},n.fn.detach=n.fn.remove,["width","height"].forEach(function(e){var i=e.replace(/./,function(t){return t[0].toUpperCase()});n.fn[e]=function(r){var o,s=this[0];return r===t?_(s)?s["inner"+i]:$(s)?s.documentElement["scroll"+i]:(o=this.offset())&&o[e]:this.each(function(t){s=n(this),s.css(e,J(this,r,t,s[e]()))})}}),v.forEach(function(t,e){var i=e%2;n.fn[t]=function(){var t,o,r=n.map(arguments,function(e){return t=L(e),"object"==t||"array"==t||null==e?e:T.fragment(e)}),s=this.length>1;return r.length<1?this:this.each(function(t,u){o=i?u:u.parentNode,u=0==e?u.nextSibling:1==e?u.firstChild:2==e?u:null;var f=n.contains(a.documentElement,o);r.forEach(function(t){if(s)t=t.cloneNode(!0);else if(!o)return n(t).remove();o.insertBefore(t,u),f&&G(t,function(t){null==t.nodeName||"SCRIPT"!==t.nodeName.toUpperCase()||t.type&&"text/javascript"!==t.type||t.src||window.eval.call(window,t.innerHTML)})})})},n.fn[i?t+"To":"insert"+(e?"Before":"After")]=function(e){return n(e)[t](this),this}}),T.Z.prototype=n.fn,T.uniq=N,T.deserializeValue=Y,n.zepto=T,n}();window.Zepto=Zepto,void 0===window.$&&(window.$=Zepto),function(t){function l(t){return t._zid||(t._zid=e++)}function h(t,e,n,i){if(e=p(e),e.ns)var r=d(e.ns);return(s[l(t)]||[]).filter(function(t){return!(!t||e.e&&t.e!=e.e||e.ns&&!r.test(t.ns)||n&&l(t.fn)!==l(n)||i&&t.sel!=i)})}function p(t){var e=(""+t).split(".");return{e:e[0],ns:e.slice(1).sort().join(" ")}}function d(t){return new RegExp("(?:^| )"+t.replace(" "," .* ?")+"(?: |$)")}function m(t,e){return t.del&&!u&&t.e in f||!!e}function g(t){return c[t]||u&&f[t]||t}function v(e,i,r,o,a,u,f){var h=l(e),d=s[h]||(s[h]=[]);i.split(/\s/).forEach(function(i){if("ready"==i)return t(document).ready(r);var s=p(i);s.fn=r,s.sel=a,s.e in c&&(r=function(e){var n=e.relatedTarget;return!n||n!==this&&!t.contains(this,n)?s.fn.apply(this,arguments):void 0}),s.del=u;var l=u||r;s.proxy=function(t){if(t=j(t),!t.isImmediatePropagationStopped()){t.data=o;var i=l.apply(e,t._args==n?[t]:[t].concat(t._args));return i===!1&&(t.preventDefault(),t.stopPropagation()),i}},s.i=d.length,d.push(s),"addEventListener"in e&&e.addEventListener(g(s.e),s.proxy,m(s,f))})}function y(t,e,n,i,r){var o=l(t);(e||"").split(/\s/).forEach(function(e){h(t,e,n,i).forEach(function(e){delete s[o][e.i],"removeEventListener"in t&&t.removeEventListener(g(e.e),e.proxy,m(e,r))})})}function j(e,i){return(i||!e.isDefaultPrevented)&&(i||(i=e),t.each(E,function(t,n){var r=i[t];e[t]=function(){return this[n]=x,r&&r.apply(i,arguments)},e[n]=b}),(i.defaultPrevented!==n?i.defaultPrevented:"returnValue"in i?i.returnValue===!1:i.getPreventDefault&&i.getPreventDefault())&&(e.isDefaultPrevented=x)),e}function S(t){var e,i={originalEvent:t};for(e in t)w.test(e)||t[e]===n||(i[e]=t[e]);return j(i,t)}var n,e=1,i=Array.prototype.slice,r=t.isFunction,o=function(t){return"string"==typeof t},s={},a={},u="onfocusin"in window,f={focus:"focusin",blur:"focusout"},c={mouseenter:"mouseover",mouseleave:"mouseout"};a.click=a.mousedown=a.mouseup=a.mousemove="MouseEvents",t.event={add:v,remove:y},t.proxy=function(e,n){var s=2 in arguments&&i.call(arguments,2);if(r(e)){var a=function(){return e.apply(n,s?s.concat(i.call(arguments)):arguments)};return a._zid=l(e),a}if(o(n))return s?(s.unshift(e[n],e),t.proxy.apply(null,s)):t.proxy(e[n],e);throw new TypeError("expected function")},t.fn.bind=function(t,e,n){return this.on(t,e,n)},t.fn.unbind=function(t,e){return this.off(t,e)},t.fn.one=function(t,e,n,i){return this.on(t,e,n,i,1)};var x=function(){return!0},b=function(){return!1},w=/^([A-Z]|returnValue$|layer[XY]$)/,E={preventDefault:"isDefaultPrevented",stopImmediatePropagation:"isImmediatePropagationStopped",stopPropagation:"isPropagationStopped"};t.fn.delegate=function(t,e,n){return this.on(e,t,n)},t.fn.undelegate=function(t,e,n){return this.off(e,t,n)},t.fn.live=function(e,n){return t(document.body).delegate(this.selector,e,n),this},t.fn.die=function(e,n){return t(document.body).undelegate(this.selector,e,n),this},t.fn.on=function(e,s,a,u,f){var c,l,h=this;return e&&!o(e)?(t.each(e,function(t,e){h.on(t,s,a,e,f)}),h):(o(s)||r(u)||u===!1||(u=a,a=s,s=n),(r(a)||a===!1)&&(u=a,a=n),u===!1&&(u=b),h.each(function(n,r){f&&(c=function(t){return y(r,t.type,u),u.apply(this,arguments)}),s&&(l=function(e){var n,o=t(e.target).closest(s,r).get(0);return o&&o!==r?(n=t.extend(S(e),{currentTarget:o,liveFired:r}),(c||u).apply(o,[n].concat(i.call(arguments,1)))):void 0}),v(r,e,u,a,s,l||c)}))},t.fn.off=function(e,i,s){var a=this;return e&&!o(e)?(t.each(e,function(t,e){a.off(t,i,e)}),a):(o(i)||r(s)||s===!1||(s=i,i=n),s===!1&&(s=b),a.each(function(){y(this,e,s,i)}))},t.fn.trigger=function(e,n){return e=o(e)||t.isPlainObject(e)?t.Event(e):j(e),e._args=n,this.each(function(){e.type in f&&"function"==typeof this[e.type]?this[e.type]():"dispatchEvent"in this?this.dispatchEvent(e):t(this).triggerHandler(e,n)})},t.fn.triggerHandler=function(e,n){var i,r;return this.each(function(s,a){i=S(o(e)?t.Event(e):e),i._args=n,i.target=a,t.each(h(a,e.type||e),function(t,e){return r=e.proxy(i),i.isImmediatePropagationStopped()?!1:void 0})}),r},"focusin focusout focus blur load resize scroll unload click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select keydown keypress keyup error".split(" ").forEach(function(e){t.fn[e]=function(t){return 0 in arguments?this.bind(e,t):this.trigger(e)}}),t.Event=function(t,e){o(t)||(e=t,t=e.type);var n=document.createEvent(a[t]||"Events"),i=!0;if(e)for(var r in e)"bubbles"==r?i=!!e[r]:n[r]=e[r];return n.initEvent(t,i,!0),j(n)}}(Zepto),function(t){function h(e,n,i){var r=t.Event(n);return t(e).trigger(r,i),!r.isDefaultPrevented()}function p(t,e,i,r){return t.global?h(e||n,i,r):void 0}function d(e){e.global&&0===t.active++&&p(e,null,"ajaxStart")}function m(e){e.global&&!--t.active&&p(e,null,"ajaxStop")}function g(t,e){var n=e.context;return e.beforeSend.call(n,t,e)===!1||p(e,n,"ajaxBeforeSend",[t,e])===!1?!1:void p(e,n,"ajaxSend",[t,e])}function v(t,e,n,i){var r=n.context,o="success";n.success.call(r,t,o,e),i&&i.resolveWith(r,[t,o,e]),p(n,r,"ajaxSuccess",[e,n,t]),x(o,e,n)}function y(t,e,n,i,r){var o=i.context;i.error.call(o,n,e,t),r&&r.rejectWith(o,[n,e,t]),p(i,o,"ajaxError",[n,i,t||e]),x(e,n,i)}function x(t,e,n){var i=n.context;n.complete.call(i,e,t),p(n,i,"ajaxComplete",[e,n]),m(n)}function b(){}function w(t){return t&&(t=t.split(";",2)[0]),t&&(t==f?"html":t==u?"json":s.test(t)?"script":a.test(t)&&"xml")||"text"}function E(t,e){return""==e?t:(t+"&"+e).replace(/[&?]{1,2}/,"?")}function j(e){e.processData&&e.data&&"string"!=t.type(e.data)&&(e.data=t.param(e.data,e.traditional)),!e.data||e.type&&"GET"!=e.type.toUpperCase()||(e.url=E(e.url,e.data),e.data=void 0)}function S(e,n,i,r){return t.isFunction(n)&&(r=i,i=n,n=void 0),t.isFunction(i)||(r=i,i=void 0),{url:e,data:n,success:i,dataType:r}}function C(e,n,i,r){var o,s=t.isArray(n),a=t.isPlainObject(n);t.each(n,function(n,u){o=t.type(u),r&&(n=i?r:r+"["+(a||"object"==o||"array"==o?n:"")+"]"),!r&&s?e.add(u.name,u.value):"array"==o||!i&&"object"==o?C(e,u,i,n):e.add(n,u)})}var i,r,e=0,n=window.document,o=/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,s=/^(?:text|application)\/javascript/i,a=/^(?:text|application)\/xml/i,u="application/json",f="text/html",c=/^\s*$/,l=n.createElement("a");l.href=window.location.href,t.active=0,t.ajaxJSONP=function(i,r){if(!("type"in i))return t.ajax(i);var f,h,o=i.jsonpCallback,s=(t.isFunction(o)?o():o)||"jsonp"+ ++e,a=n.createElement("script"),u=window[s],c=function(e){t(a).triggerHandler("error",e||"abort")},l={abort:c};return r&&r.promise(l),t(a).on("load error",function(e,n){clearTimeout(h),t(a).off().remove(),"error"!=e.type&&f?v(f[0],l,i,r):y(null,n||"error",l,i,r),window[s]=u,f&&t.isFunction(u)&&u(f[0]),u=f=void 0}),g(l,i)===!1?(c("abort"),l):(window[s]=function(){f=arguments},a.src=i.url.replace(/\?(.+)=\?/,"?$1="+s),n.head.appendChild(a),i.timeout>0&&(h=setTimeout(function(){c("timeout")},i.timeout)),l)},t.ajaxSettings={type:"GET",beforeSend:b,success:b,error:b,complete:b,context:null,global:!0,xhr:function(){return new window.XMLHttpRequest},accepts:{script:"text/javascript, application/javascript, application/x-javascript",json:u,xml:"application/xml, text/xml",html:f,text:"text/plain"},crossDomain:!1,timeout:0,processData:!0,cache:!0},t.ajax=function(e){var a,o=t.extend({},e||{}),s=t.Deferred&&t.Deferred();for(i in t.ajaxSettings)void 0===o[i]&&(o[i]=t.ajaxSettings[i]);d(o),o.crossDomain||(a=n.createElement("a"),a.href=o.url,a.href=a.href,o.crossDomain=l.protocol+"//"+l.host!=a.protocol+"//"+a.host),o.url||(o.url=window.location.toString()),j(o);var u=o.dataType,f=/\?.+=\?/.test(o.url);if(f&&(u="jsonp"),o.cache!==!1&&(e&&e.cache===!0||"script"!=u&&"jsonp"!=u)||(o.url=E(o.url,"_="+Date.now())),"jsonp"==u)return f||(o.url=E(o.url,o.jsonp?o.jsonp+"=?":o.jsonp===!1?"":"callback=?")),t.ajaxJSONP(o,s);var C,h=o.accepts[u],p={},m=function(t,e){p[t.toLowerCase()]=[t,e]},x=/^([\w-]+:)\/\//.test(o.url)?RegExp.$1:window.location.protocol,S=o.xhr(),T=S.setRequestHeader;if(s&&s.promise(S),o.crossDomain||m("X-Requested-With","XMLHttpRequest"),m("Accept",h||"*/*"),(h=o.mimeType||h)&&(h.indexOf(",")>-1&&(h=h.split(",",2)[0]),S.overrideMimeType&&S.overrideMimeType(h)),(o.contentType||o.contentType!==!1&&o.data&&"GET"!=o.type.toUpperCase())&&m("Content-Type",o.contentType||"application/x-www-form-urlencoded"),o.headers)for(r in o.headers)m(r,o.headers[r]);if(S.setRequestHeader=m,S.onreadystatechange=function(){if(4==S.readyState){S.onreadystatechange=b,clearTimeout(C);var e,n=!1;if(S.status>=200&&S.status<300||304==S.status||0==S.status&&"file:"==x){u=u||w(o.mimeType||S.getResponseHeader("content-type")),e=S.responseText;try{"script"==u?(1,eval)(e):"xml"==u?e=S.responseXML:"json"==u&&(e=c.test(e)?null:t.parseJSON(e))}catch(i){n=i}n?y(n,"parsererror",S,o,s):v(e,S,o,s)}else y(S.statusText||null,S.status?"error":"abort",S,o,s)}},g(S,o)===!1)return S.abort(),y(null,"abort",S,o,s),S;if(o.xhrFields)for(r in o.xhrFields)S[r]=o.xhrFields[r];var N="async"in o?o.async:!0;S.open(o.type,o.url,N,o.username,o.password);for(r in p)T.apply(S,p[r]);return o.timeout>0&&(C=setTimeout(function(){S.onreadystatechange=b,S.abort(),y(null,"timeout",S,o,s)},o.timeout)),S.send(o.data?o.data:null),S},t.get=function(){return t.ajax(S.apply(null,arguments))},t.post=function(){var e=S.apply(null,arguments);return e.type="POST",t.ajax(e)},t.getJSON=function(){var e=S.apply(null,arguments);return e.dataType="json",t.ajax(e)},t.fn.load=function(e,n,i){if(!this.length)return this;var a,r=this,s=e.split(/\s/),u=S(e,n,i),f=u.success;return s.length>1&&(u.url=s[0],a=s[1]),u.success=function(e){r.html(a?t("<div>").html(e.replace(o,"")).find(a):e),f&&f.apply(r,arguments)},t.ajax(u),this};var T=encodeURIComponent;t.param=function(e,n){var i=[];return i.add=function(e,n){t.isFunction(n)&&(n=n()),null==n&&(n=""),this.push(T(e)+"="+T(n))},C(i,e,n),i.join("&").replace(/%20/g,"+")}}(Zepto),function(t){t.fn.serializeArray=function(){var e,n,i=[],r=function(t){return t.forEach?t.forEach(r):void i.push({name:e,value:t})};return this[0]&&t.each(this[0].elements,function(i,o){n=o.type,e=o.name,e&&"fieldset"!=o.nodeName.toLowerCase()&&!o.disabled&&"submit"!=n&&"reset"!=n&&"button"!=n&&"file"!=n&&("radio"!=n&&"checkbox"!=n||o.checked)&&r(t(o).val())}),i},t.fn.serialize=function(){var t=[];return this.serializeArray().forEach(function(e){t.push(encodeURIComponent(e.name)+"="+encodeURIComponent(e.value))}),t.join("&")},t.fn.submit=function(e){if(0 in arguments)this.bind("submit",e);else if(this.length){var n=t.Event("submit");this.eq(0).trigger(n),n.isDefaultPrevented()||this.get(0).submit()}return this}}(Zepto),function(t){"__proto__"in{}||t.extend(t.zepto,{Z:function(e,n){return e=e||[],t.extend(e,t.fn),e.selector=n||"",e.__Z=!0,e},isZ:function(e){return"array"===t.type(e)&&"__Z"in e}});try{getComputedStyle(void 0)}catch(e){var n=getComputedStyle;window.getComputedStyle=function(t){try{return n(t)}catch(e){return null}}}}(Zepto);;
var org = (function(){
    document.body.addEventListener('touchstart', function () { }); //ios 触发active渲染
    var lib = {
        scriptName: 'mobile.js',
        _ajax :function(options){
            $.ajax({
                url: options.url,
                type: options.type,
                data: options.data,
                dataType : options.dataType,
                beforeSend: function(xhr, settings) {
                    options.beforeSend && options.beforeSend(xhr);
                    //django配置post请求
                    if (!lib._csrfSafeMethod(settings.type) && lib._sameOrigin(settings.url)) {
                      xhr.setRequestHeader('X-CSRFToken', lib._getCookie('csrftoken'));
                    }
                },
                success:function(data){
                    options.success && options.success(data);
                },
                error: function (xhr) {
                    options.error && options.error(xhr);
                },
                complete:function(){
                    options.complete && options.complete();
                }
            });
        },
        _calculate :function(dom, callback){
            var calculate = function(amount, rate, period, pay_method) {
                var divisor, rate_pow, result, term_amount;
                if (/等额本息/ig.test(pay_method)) {
                    rate_pow = Math.pow(1 + rate, period);
                    divisor = rate_pow - 1;
                    term_amount = amount * (rate * rate_pow) / divisor;
                    result = term_amount * period - amount;
                } else if (/日计息/ig.test(pay_method)) {
                    result = amount * rate * period / 360;
                } else {
                    result = amount * rate * period / 12;
                }
                return Math.floor(result * 100) / 100;
            };
            dom.on('input', function(e) {
                var earning, earning_element, earning_elements, fee_earning, fee_element, fee_elements;
                var target = $(e.target),
                    existing = parseFloat(target.attr('data-existing')),
                    period = target.attr('data-period'),
                    rate = target.attr('data-rate')/100,
                    pay_method = target.attr('data-paymethod');
                    activity_rate = target.attr('activity-rate')/100;
                    amount = parseFloat(target.val()) || 0;

                if (amount > target.attr('data-max')) {
                    amount = target.attr('data-max');
                    target.val(amount);
                }
                amount = parseFloat(existing) + parseFloat(amount);
                earning = calculate(amount, rate, period, pay_method);
                fee_earning = calculate(amount, activity_rate, period, pay_method);

                if (earning < 0) {
                    earning = 0;
                }
                earning_elements = (target.attr('data-target')).split(',');

                for (var i = 0; i < earning_elements.length; i ++) {
                    earning_element = earning_elements[i];
                    if (earning) {
                        fee_earning = fee_earning ? fee_earning : 0;
                        earning += fee_earning;
                        $(earning_element).text(earning.toFixed(2));
                    } else {
                        $(earning_element).text("0.00");
                    }
                }

                callback && callback(target);
            });
        },
        _getQueryStringByName:function(name){
            var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
             if(result == null || result.length < 1){
                 return '';
             }
             return result[1];
        },
        _getCookie :function(name){
            var cookie, cookieValue, cookies, i;
                cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    cookies = document.cookie.split(';');
                    i = 0;
                    while (i < cookies.length) {
                      cookie = $.trim(cookies[i]);
                      if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                      }
                      i++;
                    }
                }
              return cookieValue;
        },
        _csrfSafeMethod :function(method){
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        },
        _sameOrigin:function(url){
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = '//' + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
        },
        _setShareData:function(ops,suFn,canFn){
            var setData = {};
            if(typeof ops == 'object'){
                for(var p in ops){
                    setData[p] = ops[p];
                }
            }
            typeof suFn =='function' && suFn != 'undefined' ? setData.success = suFn : '';
            typeof canFn =='function' && canFn != 'undefined' ? setData.cancel = canFn : '';
            return setData
        },
        /*
         * 分享到微信朋友
         */
        _onMenuShareAppMessage:function(ops,suFn,canFn){
            wx.onMenuShareAppMessage(lib._setShareData(ops,suFn,canFn));
        },
        /*
         * 分享到微信朋友圈
         */
        _onMenuShareTimeline:function(ops,suFn,canFn){
            wx.onMenuShareTimeline(lib._setShareData(ops,suFn,canFn));
        },
        _onMenuShareQQ:function(){
            wx.onMenuShareQQ(lib._setShareData(ops,suFn,canFn));
        }
    }
    return {
        scriptName             : lib.scriptName,
        ajax                   : lib._ajax,
        calculate              : lib._calculate,
        getQueryStringByName   : lib._getQueryStringByName,
        getCookie              : lib._getCookie,
        csrfSafeMethod         : lib._csrfSafeMethod,
        sameOrigin             : lib._sameOrigin,
        onMenuShareAppMessage  : lib._onMenuShareAppMessage,
        onMenuShareTimeline    : lib._onMenuShareTimeline,
        onMenuShareQQ          : lib._onMenuShareQQ,
    }
})();

org.ui = (function(){
    var lib = {
        _alert: function(txt, callback){
            if(document.getElementById("alert-cont")){
                document.getElementById("alertTxt").innerHTML = txt;
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
            }else{
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText="position:absolute;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
                var alertFram = document.createElement("DIV");
                alertFram.id="alert-cont";
                alertFram.style.cssText="position:absolute; top:35%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
                strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 1.25rem .75rem;'>"+txt+"</div>";
                strHtml += " <div class='popub-footer' style='width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;'>确认</div>";
                alertFram.innerHTML = strHtml;
                document.body.appendChild(alertFram);
                document.body.appendChild(shield);

                $('.popub-footer').on('click',function(){
                    alertFram.style.display = "none";
                    shield.style.display = "none";
                    callback && callback();
                })
            }
            document.body.onselectstart = function(){return false;};
        },
        _showSign:function(signTxt, callback){
            var $sign = $('.error-sign');
            if($sign.length == 0){
                $('body').append("<section class='error-sign'>" + signTxt + "</section>");
                $sign = $('.error-sign');
            }else{
                $sign.text(signTxt)
            }
            ~function animate(){
                $sign.css('display','block');
                setTimeout(function(){
                    $sign.css('opacity', 1);
                    setTimeout(function(){
                        $sign.css('opacity', 0);
                        setTimeout(function(){
                            $sign.hide();
                            return callback && callback();
                        },300)
                    },1000)
                },0)
            }()
        },
        /*
          .form-list
              .form-icon.user-phone(ui targer).identifier-icon（事件target）
              .form-input
                input(type="tel", name="identifier", placeholder="请输入手机号",data-target2='identifier-icon'（事件target）, data-icon='user-phone'(ui事件), data-target="identifier-edit"(右侧操作), data-empty=''（input val空的时候的classname）, data-val='input-clear'（input val不为空的时候的classname）).foreach-input
                .form-edit-icon.identifier-edit（右边操作如：清空密码）
         */
        _inputStyle:function(options){
            var $submit = options.submit,
                inputArrList = options.inputList;

            $.each(inputArrList, function(i){
                inputArrList[i]['target'].on('input',function(){
                    var $self = $(this);
                    if($self.val() == ''){
                        inputForClass([
                            { target: $self.attr('data-target'), addName : $self.attr('data-empty'), reMove : $self.attr('data-val')},
                            { target: $self.attr('data-target2'), addName : $self.attr('data-icon'), reMove : ($self.attr('data-icon')+"-active")},
                        ])
                        $submit.attr('disabled', true);
                    }else{
                        inputForClass([
                            { target: $self.attr('data-target'), addName : $self.attr('data-val'),reMove : $self.attr('data-empty')},
                            { target: $self.attr('data-target2'), addName : ($self.attr('data-icon')+"-active"), reMove : $self.attr('data-icon')}
                        ])
                    }
                    canSubmit() ? $submit.css('background','rgba(219,73,63,1)').removeAttr('disabled') : $submit.css('background','rgba(219,73,63,.5)').attr('disabled')
                })
            })

            //用户名一键清空
            $('.identifier-edit').on('click', function(e){
                $(this).siblings().val('').trigger('input');
            })
            //密码隐藏显示
            $('.password-handle').on('click',function(){
                if($(this).hasClass('hide-password')){
                    $(this).addClass('show-password').removeClass('hide-password');
                    $(this).siblings().attr('type','text');
                }else if($(this).hasClass('show-password')){
                    $(this).addClass('hide-password').removeClass('show-password');
                    $(this).siblings().attr('type','password');
                }
            })

            var inputForClass = function(ops){
                if(!typeof(ops) === 'object') return ;
                $.each(ops, function(i){
                    $('.'+ops[i].target).addClass(ops[i].addName).removeClass(ops[i].reMove);
                })
            }
            var returnCheckArr = function(){
                var returnArr = [];
                for(var i = 0; i < arguments.length; i++){
                    for(var arr in arguments[i]){
                        if(arguments[i][arr]['required'])
                          returnArr.push(arguments[i][arr]['target'])
                    }
                }
                return returnArr
            }
            var canSubmit = function(){
                var isPost = true, newArr = [];

                newArr = returnCheckArr(options.inputList, options.otherTarget);

                $.each(newArr, function(i, dom){
                    if(dom.attr('type') == 'checkbox'){
                        if (!dom.attr('checked'))
                            return  isPost =  false
                    }else if (dom.val() == '')
                        return  isPost =  false
                })

                return isPost
            }
        },
    }

    return {
        focusInput: lib._inputStyle,
        showSign : lib._showSign,
        alert : lib._alert,
    }
})();


org.login = (function(org){
    var lib = {
        $captcha_img : $('#captcha'),
        $captcha_key : $('input[name=captcha_0]'),
        init:function(){
            lib._captcha_refresh();
            lib._checkFrom();
        },
        _captcha_refresh :function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function(res) {
                lib.$captcha_img.attr('src', res['image_url']);
                lib.$captcha_key.val(res['key']);
            });
        },
        _checkFrom:function(){
            var $form = $('#login-form'),
                $submit = $form.find('button[type=submit]');
            org.ui.focusInput({
                submit : $('button[type=submit]'),
                inputList: [
                    {target : $('input[name=identifier]'),  required:true},
                    {target : $('input[name=password]'), required : true},
                    {target: $('input[name=captcha_1]'), required : true},
                ],
            });

            //刷新验证码
            lib.$captcha_img.on('click', function() {
                lib._captcha_refresh();
            });
            $submit.on('click', function() {
                var data = {
                    'identifier': $.trim($form.find('input[name=identifier]').val()),
                    'password': $.trim($form.find('input[name=password]').val()),
                    'captcha_0': $.trim($form.find('input[name=captcha_0]').val()),
                    'captcha_1': $.trim($form.find('input[name=captcha_1]').val()),
                    'openid': $.trim($form.find('input[name=openid]').val())
                }
                org.ajax({
                    'type': 'post',
                    'url': $form.attr('action'),
                    'data': data,
                    beforeSend: function (xhr) {
                        $submit.attr('disabled', true).text('登录中..');
                    },
                    success: function(res) {
                        var next = org.getQueryStringByName('next');
                        if (next) {
                            window.location.href = decodeURIComponent(decodeURIComponent(next));;
                        }else{
                            window.location.href = '/weixin/account/';
                        }
                    },
                    error: function(res) {
                        if (res['status'] == 403) {
                            org.ui.showSign('请勿重复提交')
                            return false;
                        }
                        var data = JSON.parse(res.responseText);
                        for (var key in data) {
                            data['__all__'] ?  org.ui.showSign(data['__all__']) : org.ui.showSign(data[key]);
                        }
                        lib._captcha_refresh()
                    },
                    complete: function() {
                        $submit.removeAttr('disabled').text('登录网利宝');
                    }
                });
                return false;
            });
        }
    }
    return {
        init : lib.init
    }


})(org);

org.regist = (function(org){
    var lib ={
        $captcha_img : $('#captcha'),
        $captcha_key : $('input[name=captcha_0]'),
        init:function(){
            lib._captcha_refresh();
            lib._checkFrom();
            lib._animateXieyi();
        },
        _animateXieyi:function(){
            var $submitBody = $('.submit-body'),
                $protocolDiv = $('.regist-protocol-div'),
                $cancelXiyi = $('.cancel-xiyie'),
                $showXiyi = $('.xieyi-btn'),
                $agreement = $('#agreement');
            //是否同意协议
            $agreement.change(function() {
              if ($(this).attr('checked') == 'checked') {
                $submitBody.addClass('disabled').attr('disabled', 'disabled');
                return $(this).removeAttr('checked');
              } else {
                $submitBody.removeClass('disabled').removeAttr('disabled');
                return $(this).attr('checked', 'checked');
              }
            });
            //显示协议
            $showXiyi.on('click',function(event){
                event.preventDefault();
                $protocolDiv.css('display','block');
                setTimeout(function(){
                    $protocolDiv.css('top','0%');
                },0)
            })
            //关闭协议
            $cancelXiyi.on('click',function(){
                $protocolDiv.css('top','100%');
                setTimeout(function(){
                    $protocolDiv.css('display','none');
                },200)
            })
        },
        _captcha_refresh :function(){
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function(res) {
                lib.$captcha_img.attr('src', res['image_url']);
                lib.$captcha_key.val(res['key']);
            });
        },
        _checkFrom:function(){
            var $submit = $('button[type=submit]'),
                $identifier = $('input[name=identifier]'),
                $password = $('input[name=password]'),
                $validation =  $('input[name=validation]'),
                $invitation = $('input[name=invitation]'),
                $agreement = $('input[name=agreement]'),
                $captcha_0 =  $('input[name=captcha_0]'),
                $captcha_1 =  $('input[name=captcha_1]');


            org.ui.focusInput({
                submit : $submit,
                inputList: [
                    {target : $identifier,  required:true},
                    {target :$password,required : true},
                    {target: $validation,required : true},
                    {target: $invitation, required: false},
                    {target: $captcha_1, required: true}
                ],
                otherTarget : [{target: $agreement,required: true}]
            });
            $("#agreement").on('click',function(){
                $(this).toggleClass('agreement');
                $(this).hasClass('agreement') ?  $(this).find('input').attr('checked','checked') : $(this).find('input').removeAttr('checked');
                $identifier.trigger('input')
            })
            //刷新验证码
            lib.$captcha_img.on('click', function() {
                lib._captcha_refresh();
            });


            //手机验证码
            $('.request-check').on('click',function(){
                var phoneNumber = $identifier.val(),
                    $that = $(this), //保存指针
                    count = 60,  //60秒倒计时
                    intervalId ; //定时器

                if(!check['identifier'](phoneNumber, 'phone')) return  //号码不符合退出
                $that.attr('disabled', 'disabled').addClass('regist-alreay-request');
                org.ajax({
                    url : '/api/phone_validation_code/register/' + phoneNumber + '/',
                    data: {
                        captcha_0 : $captcha_0.val(),
                        captcha_1 : $captcha_1.val(),
                    },
                    type : 'POST',
                    error :function(xhr){
                        clearInterval(intervalId);
                        var result = JSON.parse(xhr.responseText);
                        org.ui.showSign(result.message);
                        $that.text('获取验证码').removeAttr('disabled').removeClass('regist-alreay-request');
                        lib._captcha_refresh();
                    }
                });
                //倒计时
                var timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return $that.text( count + '秒后可重发');
                    } else {
                        clearInterval(intervalId);
                        $that.text('重新获取').removeAttr('disabled').removeClass('regist-alreay-request');
                        return lib._captcha_refresh();
                    }
                };
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            });
            //校验方法
            var check ={
                identifier:function(val){
                    var isRight = false,
                        re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
                    re.test($.trim(val)) ? isRight = true : (org.ui.showSign('请输入正确的手机号'),isRight = false);
                    return isRight;
                },
                password:function(val){
                   if(6 > $.trim(val).length || $.trim(val).length > 20 ){
                       org.ui.showSign('密码为6-20位数字/字母/符号/区分大小写')
                       return false
                   }
                   return true
                }
            }
            var checkList = [$identifier, $password],
                isSubmit = true;

            $submit.on('click',function(){
                isSubmit =  true;
                //校验主函数
                $.each(checkList, function(){
                    var value = $(this).val(), checkTarget = $(this).attr('name');
                    if(!check[checkTarget](value)){
                        return isSubmit = false
                    }
                })

                if(!isSubmit) return false
                var tid = org.getQueryStringByName('tid');
                var token = $invitation.val() === '' ?  $('input[name=token]').val() : $invitation.val();
                org.ajax({
                    url: '/api/register/',
                    type: 'POST',
                    data: {
                            'identifier':       $identifier.val(),
                            'password':         $password.val(),
                            'captcha_0':        $captcha_0.val(),
                            'captcha_1':        $captcha_1.val(),
                            'validate_code':    $validation.val(),
                            'invite_code':      token,
                            'tid' : tid,
                    },
                    beforeSend: function() {
                        $submit.text('注册中,请稍等...');
                    },
                    success:function(data){
                        if(data.ret_code === 0){
                            var next = org.getQueryStringByName('next') == '' ? '/weixin/regist/succees/' : org.getQueryStringByName('next');
                            next = org.getQueryStringByName('mobile') == '' ? next : next + '&mobile='+ org.getQueryStringByName('mobile');
                            next = org.getQueryStringByName('serverId') == '' ? next : next + '&serverId='+ org.getQueryStringByName('serverId');
                            window.location.href = next;
                        }else if(data.ret_code > 0){
                            org.ui.showSign(data.message)
                            $submit.text('立即注册 ｜ 领取奖励');
                        }
                    },
                    error: function (xhr) {
                        var result = JSON.parse(xhr.responseText);
                        if(xhr.status === 429){
                            org.ui.alert('系统繁忙，请稍候重试')
                        }else{
                            org.ui.alert(result.message);
                        }
                    },
                    complete:function(){
                        $submit.text('立即注册 ｜ 领取奖励');
                    }
                });
            })
        }
    }
    return {
        init : lib.init
    }
})(org);

org.list = (function(org){
    var lib = {
        windowHeight : $(window).height(),
        canGetPage : true, //防止多次请求
        scale : 0.8, //页面滚到百分70的时候请求
        pageSize: 10, //每次请求的个数
        page: 2, //从第二页开始
        init :function(){
            lib._swiper();
            lib._scrollListen();
        },
        _swiper:function(){
            var autoplay = 5000, //焦点图切换时间
                loop = true,  //是否无缝滚动
                $swiperSlide = $('.swiper-slide');

            if($swiperSlide.length/2 < 1){
                autoplay= 0;
                loop = false;
            }
            var myswiper = new Swiper('.swiper-container', {
                pagination: '.swiper-pagination',
                loop: loop,
                lazyLoading: true,
                autoplay: autoplay,
                autoplayDisableOnInteraction: true,

            });
        },
        _scrollListen:function(){
            $(document).scroll(function(){
                if(document.body.scrollTop / (document.body.clientHeight -lib.windowHeight ) >= lib.scale){
                    lib.canGetPage && lib._getNextPage();
                }
            });
        },
        _getNextPage :function(){
            org.ajax({
                type: 'GET',
                url: '/api/p2ps/wx/',
                data: {page: lib.page, 'pagesize': lib.pageSize},
                beforeSend:function(){
                    lib.canGetPage =false
                },
                success: function(data){
                   $('#list-body').append(data.html_data);
                    lib.page++;
                    lib.canGetPage = true;
                },
                error: function(){
                    org.ui.alert('Ajax error!')
                }
            })
        }

    };
    return {
        init : lib.init
    }
})(org);

org.detail = (function(org){
    var lib ={
        weiURL: '/weixin/api/jsapi_config/',
        countDown: $('#countDown'),
        init :function(){
            lib._tab();
            lib._animate();
            lib._share();
            lib.countDown.length > 0 && lib._countDown(lib.countDown)
        },
        /*
        * 页面动画
         */
        _animate:function(){
            $(function(){
                var $progress = $('.progress-percent')
                $payalert = $('.new-pay');
                setTimeout(function(){
                    var percent = parseFloat($progress.attr('data-percent'));
                    if(percent == 100){
                        $progress.css('margin-top','-10%');
                    }else{
                        $progress.css('margin-top', (100 - percent) + '%');
                    }
                    setTimeout(function(){
                        $progress.addClass('progress-bolang')
                    },1000)
                },300)
            })
        },
        /*
        * 公司信息tab
         */
        _tab:function(){
            $('.toggleTab').on('click',function(){
                $(this).siblings().toggle();
                $(this).find('span').toggleClass('icon-rotate');
            })
        },
        /*
        * 微信分享
         */
        _share: function(){
            var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
            org.ajax({
                type : 'GET',
                url : lib.weiURL,
                dataType : 'json',
                success : function(data) {
                    //请求成功，通过config注入配置信息,
                    wx.config({
                        debug: false,
                        appId: data.appId,
                        timestamp: data.timestamp,
                        nonceStr: data.nonceStr,
                        signature: data.signature,
                        jsApiList: jsApiList
                    });
                }
            });
            wx.ready(function(){
                var $productName = $('.product-name'),
                    $earningRate = $('.profit-txt'),
                    $period = $('.time-txt');

                var host = 'https://www.wanglibao.com',
                    shareName = $productName.attr('data-name'),
                    shareImg = host + '/static/imgs/mobile/share_logo.png',
                    shareLink = host + '/weixin/detail/'+$productName.attr('data-productID'),
                    shareMainTit = '我在网利宝发现一个不错的投资标的，快来看看吧',
                    shareBody = shareName + ',年收益' + $earningRate.attr('data-earn') + '%,期限' + $period.attr('data-period');
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg
                });
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: shareMainTit,
                    link : shareLink,
                    imgUrl: shareImg
                })
                //分享给QQ
                org.onMenuShareQQ({
                    title: shareMainTit,
                    desc: shareBody,
                    link : shareLink,
                    imgUrl: shareImg
                })
            })
        },
        /*
        * 倒计时
         */
        _countDown:function(target){
            var endTimeList = target.attr('data-left').replace(/-/g,'/');
            var  TimeTo =function (dd){
                var t = new Date(dd),
                    n = parseInt(new Date().getTime()),
                    c = t - n;
                if( c <= 0 ){
                    target.text('活动已结束')
                    clearInterval(window['interval']);
                    return
                }
                var ds = 60*60*24*1000,
                    d = parseInt(c/ds),
                    h = parseInt((c-d*ds)/(3600*1000)),
                    m = parseInt((c - d*ds - h*3600*1000)/(60*1000)),
                    s = parseInt((c-d*ds-h*3600*1000-m*60*1000)/1000);
                    m < 10 ? m = '0' + m: '';
                    s < 10 ? s = '0' + s: '';
                    target.text(d+'天'+h+'小时'+m+'分'+s+'秒');
            }
            window['interval']= setInterval(function(){
                TimeTo(endTimeList);
            },1000);
        }
    }
    return {
        init : lib.init
    }
})(org);

org.buy=(function(org){
    var lib = {
        redPackSelect : $('#gifts-package'),
        amountInout : $('input[data-role=p2p-calculator]'),
        $redpackSign : $('.redpack-sign'),
        $redpackForAmount : $('.redpack-for-amount'),
        showredPackAmount:$(".redpack-amount"),
        showAmount :$('.need-amount'),
        redPackAmount: 0,
        isBuy: true, //防止多次请求，后期可修改布局用button的disable，代码罗辑会少一点
        init :function(){
            lib._calculate();
            lib._buy();
        },
        /*
        * 购买页收益计算器
         */
        _calculate:function(){
            org.calculate(lib.amountInout,lib._setRedpack)
        },
        /*
        *   购买提示信息
        *   触发_setRedpack条件 选择红包，投资金额大于0
        *
        *
         */
        _setRedpack:function(){
            var redPack = lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex),//选择的select项
                redPackVal = parseFloat(lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex).attr('data-amount'))
                inputAmount  =parseInt(lib.amountInout.val()), //输入框金额
                redPackAmount = redPack.attr("data-amount"), //红包金额
                redPackMethod = redPack.attr("data-method"), //红包类型
                redPackInvestamount = parseInt(redPack.attr("data-investamount")),//红包门槛
                redPackHighest_amount = parseInt(redPack.attr("data-highest_amount")),//红包最高抵扣（百分比红包才有）
                repPackDikou = 0,
                senderAmount = 0; //实际支付金额;
            lib.redPackAmountNew = 0 ;
            if(redPackVal){ //如果选择了红包
                console.log(inputAmount)
                if(!inputAmount){
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    lib.$redpackSign.hide();//红包直抵提示
                    return
                }
                if(inputAmount < redPackInvestamount){
                    lib.$redpackSign.hide();//红包直抵提示
                    lib.$redpackForAmount.hide();//请输入投资金额
                    return $(".redpack-investamount").show();//未达到红包使用门槛
                }else{
                    if(redPackMethod == '*'){ //百分比红包
                        //如果反回来的百分比需要除于100 就把下面if改成if (inputAmount * redPackAmount/100 > redPackHighest_amount)
                        if(inputAmount * redPackAmount >= redPackHighest_amount){//是否超过最高抵扣
                           repPackDikou = redPackHighest_amount;
                        }else{//没有超过最高抵扣
                            repPackDikou = inputAmount * redPackAmount;
                        }
                    }else{  //直抵红包
                        repPackDikou = parseInt(redPackAmount);
                    }
                    senderAmount = inputAmount - repPackDikou;
                    lib.redPackAmountNew = repPackDikou;
                    lib.showredPackAmount.text(repPackDikou);//红包抵扣金额
                    lib.showAmount.text(senderAmount);//实际支付金额
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    lib.$redpackSign.show();//红包直抵提示
                }
            }else{
                lib.$redpackSign.hide();//红包直抵提示
            }
            lib.$redpackForAmount.hide();//请输入投资金额

        },
        _buy:function(){
            var $buyButton = $('.snap-up'),
                $redpack = $("#gifts-package"), redpackAmount,
                reg =/^\d+(\.\d+)?$/;
            //红包select事件
            $redpack.on("change",function(){
                if($(this).val() != ''){
                    lib.amountInout.val() == '' ? $('.redpack-for-amount').show() : lib._setRedpack();
                }else{
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    lib.$redpackSign.hide();
                }
            });

            $buyButton.on('click',function(){
                var $buySufficient = $('.buy-sufficient'),
                    balance = parseFloat($("#balance").attr("data-value")),
                    amount = $('.amount').val() *1,
                    productID = $(".invest-one").attr('data-protuctid'),
                    redPackAmount = 0;
                if(amount){
                    if(amount % 100 !== 0) return org.ui.alert('请输入100的倍数金额');
                    if(amount > balance)  return $buySufficient.show();
                }else{
                     return org.ui.alert('请输入正确的金额');
                }
                var redpackValue = $redpack[0].options[$redpack[0].options.selectedIndex].value;
                if(!redpackValue || redpackValue == ''){
                    redpackValue = null;
                }else{
                    redPackAmount = parseInt(lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex).attr('data-amount'));
                    redPackAmount ? "" : redPackAmount = 0;
                }
                if(lib.isBuy){
                   if(confirm("购买金额为" + amount)){
                        org.ajax({
                            type: 'POST',
                            url: '/api/p2p/purchase/',
                            data: {product: productID, amount: amount, redpack: redpackValue},
                            beforeSend:function(){
                                $buyButton.text("抢购中...");
                                lib.isBuy = false;
                            },
                            success: function(data){
                               if(data.data){
                                   $('.balance-sign').text(balance - data.data + lib.redPackAmountNew);
                                   $(".sign-main").css("display","-webkit-box");
                               }
                            },
                            error: function(xhr){
                                var  result;
                                result = JSON.parse(xhr.responseText);
                                if(xhr.status === 400){
                                    if (result.error_number === 1) {
                                        org.ui.alert("登录超时，请重新登录！",function(){
                                            return window.location.href= '/weixin/login/?next=/weixin/view/buy/'+productID+'/';
                                        });
                                    } else if (result.error_number === 2) {
                                        return org.ui.alert('必须实名认证！');
                                    } else if (result.error_number === 4 && result.message === "余额不足") {
                                        $(".buy-sufficient").show();
                                        return;
                                    }else{
                                        return org.ui.alert(result.message);
                                    }
                                }else if(xhr.status === 403){
                                    if (result.detail) {
                                        org.ui.alert("登录超时，请重新登录！",function(){
                                            return window.location.href = '/weixin/login/?next=/weixin/view/buy/' + productID + '/';
                                        });

                                    }
                                }
                            },
                            complete:function(){
                               $buyButton.text("确定抢购");
                                lib.isBuy = true;
                            }
                        })
                   }
                }else{
                    org.ui.alert("购买中，请稍后")
                }
            })
        }
    }
    return {
        init : lib.init
    }
})(org);

org.calculator=(function(org){
    var lib = {
        init :function(){
            org.calculate($('input[data-role=p2p-calculator]'))
            lib._addEvenList();
        },
        _addEvenList:function(){
            var $calculatorBuy = $('.calculator-buy'),
                $countInput = $('.count-input'),
                productId, amount_profit, amount;

            $calculatorBuy.on('click',function(){
                productId = $(this).attr('data-productid');
                amount  = $countInput.val();
                amount_profit = $("#expected_income").text();
                if(amount % 100 !== 0 || amount == ''){
                    return org.ui.alert("请输入100的整数倍")
                }else{
                    window.location.href = '/weixin/view/buy/' + productId + '/?amount='+ amount + '&amount_profit=' + amount_profit;
                }
            })
        }

    }
    return {
        init : lib.init
    }
})(org);

org.recharge=(function(org){
    var lib = {
        canRecharge: true,
        init :function(){
            lib._getBankCardList();
            lib._rechargeStepFirst();
            lib._initBankNav();
        },
        /*
        * 充值nav动画及事件触发
        */
        _initBankNav:function(){
            var $nav = $(".bank-list-nav"),
                $cardNone = $('.card-none'),
                $cardHave = $('.card-have');
            $nav.css("-webkit-transform","translate3d(10.2rem,0,0)");
            $nav.on('click',function(e){
                var $targetName = e.target.className.split(' ')[1];
                switch ($targetName){
                    case 'bank-add':
                        closeNav(function(){
                            $cardHave.hide();
                            setTimeout(function(){
                                $cardHave.css("opacity",0)
                                $cardNone.show();
                                setTimeout(function(){
                                    $cardNone.css("opacity",1)
                                },50)
                            },50)
                        })
                        break;
                    case 'bank-card':
                        $('.recharge-select-bank').css('display','-webkit-box');
                        closeNav();
                        break;
                    case 'bank-cancel':
                        closeNav();
                        break
                }

            });
            function closeNav(callback){
                $nav.css("-webkit-transform","translate3d(10.2rem,0,0)");
                callback && callback();
            }
        },
        /*
        * 页面初始化判断是否首次充值
         */
        _getBankCardList: function(){
            var $cardNone = $('.card-none'),
                $cardHave = $('.card-have');
            org.ajax({
                type: 'POST',
                url: '/api/pay/cnp/list/',
                success: function(data) {
                      //如果支付接口有返回已绑定的银行列表，将银行列表写入网页，银行卡：data.cards
                    if(data.ret_code == 0){
                        $(".recharge-loding").hide();
                        if(data.cards.length === 0){
                            $cardNone.show();
                            setTimeout(function(){
                                $cardNone.css("opacity",1)
                            },50)
                        }else if(data.cards.length > 0){
                            lib._initCard(data.cards,lib._cradStyle(data.cards));
                            $cardHave.show();
                            setTimeout(function(){
                                $cardHave.css("opacity",1)
                            },50)
                        }
                    }
                }
            })
            $(".bank-txt-right").on('click',function(){
                    $(".bank-list-nav").css("-webkit-transform","translate3d(0,0,0)");
            })
        },
        /*
        *  初始化默认银行卡，没有默认银行卡，现在为第一个，回调函数为银行卡列表
         */
        _initCard:function(data, callback){
            $("#card-val").val(data[0]['storable_no'].slice(0,6) + '********'+ data[0]['storable_no'].slice(-4)).attr('data-storable', data[0]['storable_no']);
            $(".bank-txt-name").text(data[0]['bank_name']);
            callback && callback();
        },
        /*
        * 银行卡列表
         */
        _cradStyle:function(cardList){
            var str = '';
            for(var card in cardList){
                str += "<div class= 'select-bank-list' data-storable="+cardList[card].storable_no+">";
                str += "<div class='bank-cont'>";
                str += "<p class='bank-name-alert'>" + cardList[card].bank_name + "</p>";
                str += "<p>尾号 " + cardList[card].storable_no.slice(-4) + "</p>";
                str += "<p>限额 200000</p>";
                str += "</div>";
                str += "<div class='bank-type'>储蓄卡</div>";
                str += "</div>";
            }
            $(".select-bank-body").append(str);

            $('.select-bank-list').on('click',function(event){
                var that = this;
                $("#card-val").val($(that).attr("data-storable").slice(0,6) + '********'+ $(that).attr("data-storable").slice(-4)).attr('data-storable', $(that).attr("data-storable"));
                $(".bank-txt-name").text($(this).find(".bank-name-alert").text());
            });
            $(".recharge-select-bank").on('click',function(){
                 return $(this).hide();
            })
        },
        /*
        *   $firstBtn 为首次充值 进到一下步
        *   $secondBtn 为快捷充值
         */
        _rechargeStepFirst:function(){
            var card_no, gate_id, amount, maxamount,
                $firstBtn = $('#firstBtn'),
                $secondBtn = $('#secondBtn');

            $firstBtn.on('click', function(){
                card_no = $("input[name='card_none_card']").val(),
                gate_id = $("select[name='gate_id_none_card']").val(),
                amount  = $("input[name='amount']").val() * 1,
                maxamount = parseInt($("input[name='maxamount']").val());
                if(!card_no || !gate_id || amount <= 0 || !amount) {
                    return org.ui.alert('信息输入不完整');
                }
                if(amount > maxamount){
                     return org.ui.alert('最高充值'+ maxamount +'元！')
                }
                window.location.href = '/weixin/recharge/second/?rechargeNext='+$(this).attr('data-next')+'&card_no=' + card_no + '&gate_id=' + gate_id + '&amount=' + amount;
            });
            $secondBtn.on('click', function(){
                card_no = $("input[name='card_no']").attr('data-storable'),
                amount  = $("input[name='amount']").val() * 1,
                maxamount = parseInt($("input[name='maxamount']").val());
                if(!card_no || amount <= 0 || !amount) {
                    return org.ui.alert('信息输入不完整');
                }
                if(amount > maxamount){
                     return org.ui.alert('最高充值'+ maxamount +'元！')
                }
                if(lib.canRecharge){
                    confirm("充值金额为"+amount) && lib._rechargeSingleStep(card_no,amount);
                }else{
                    return org.ui.alert('充值中，请稍后');
                }

            });
        },
        /*
        * 快捷充值接口业务
         */
        _rechargeSingleStep: function(card_no, amount) {
            org.ajax({
                type: 'POST',
                url: '/api/pay/deposit/',
                data: {card_no: card_no, amount: amount},
                beforeSend:function(){
                    lib.canRecharge = false;
                    $('#secondBtn').text("充值中..");
                },
                success: function(data) {
                    if(data.ret_code > 0) {
                        return org.ui.alert(data.message);
                    } else {
                         $('.sign-main').css('display','-webkit-box').find(".balance-sign").text(data.amount);
                    }
                },
                error:function(data){
                    if(data.status == 403){
                        org.ui.alert('登录超时，请重新登录！');
                    }
                },
                complete:function(){
                    $('#secondBtn').text("充值");
                    lib.canRecharge = true;
                }
            })
        }
    }
    return {
        init : lib.init
    }
})(org);

/*
* 首次充值进入下一个页面的业务
 */
org.recharge_second=(function(org){
    var lib = {
        card_no : $("input[name='card_no']").val(),
        gate_id : $("input[name='gate_id']").val(),
        amount  : parseInt($("input[name='amount']").val()),
        phone: null,
        init :function(){
            lib._getValidateCode();
            lib._rechargeStepSecond();
        },
        _getValidateCode: function(){
            var getValidateBtn = $('.request-check');

            getValidateBtn.on('click', function(){
                var count = 180, intervalId ; //定时器
                var re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
                lib.phone = $("input[name='phone']").val();
                lib.card_no = $("input[name='card_no']").val();

                if(!lib.phone){
                    return org.ui.alert('请填写手机号');
                }
                if(!re.test(lib.phone)){
                    return org.ui.alert('请填写正确手机号');
                }

                getValidateBtn.attr('disabled', 'disabled').addClass('alreay-request');
                //倒计时
                var timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return getValidateBtn.text( count + '秒后可重发');
                    } else {
                        clearInterval(intervalId);
                        getValidateBtn.text('重新获取').removeAttr('disabled').removeClass('alreay-request');
                        return
                    }
                };

                org.ajax({
                    type: 'POST',
                    url: '/api/pay/deposit/',
                    data: {card_no: lib.card_no, gate_id: lib.gate_id, phone: lib.phone, amount: lib.amount},
                    success: function(data) {
                        if(data.ret_code > 0) {
                            clearInterval(intervalId);
                            getValidateBtn.text('重新获取').removeAttr('disabled').removeClass('alreay-request');
                            return org.ui.alert(data.message);
                        } else {
                            //alert('验证码已经发出，请注意查收！');
                            $("input[name='order_id']").val(data.order_id);
                            $("input[name='token']").val(data.token);
                        }
                    },
                    error:function(data){
                        console.log(data)
                    }
                })
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            })
        },
        _rechargeStepSecond:function(){
            var secondBtn = $('#secondBtn'),
                canPost = true,
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
            secondBtn.on('click', function(){
                var order_id = $("input[name='order_id']").val(),
                    vcode = $("input[name='vcode']").val(),
                    token = $("input[name='token']").val(),
                    amount = $("input[name='amount']").val();
                if(!lib.phone){
                    return org.ui.alert('请填写手机号');
                }
                if(!re.test(lib.phone)){
                    return org.ui.alert('请填写正确手机号');
                }
                if(!vcode){
                    return org.ui.alert('请输入手机验证码');
                }
                if(!order_id || !token) {
                    return org.ui.alert('系统有错误，请重试获取验证码');
                }

                if(canPost){
                    if(confirm("充值金额为" + amount)){
                        org.ajax({
                            type: 'POST',
                            url: '/api/pay/cnp/dynnum/',
                             data: {phone: lib.phone, vcode: vcode, order_id: order_id, token: token},
                            beforeSend:function(){
                                canPost = false;
                                secondBtn.text("充值中...");
                            },
                            success: function(data) {
                                if(data.ret_code > 0) {
                                    return org.ui.alert(data.message);
                                } else {
                                   $('.sign-main').css('display','-webkit-box').find(".balance-sign").text(data.amount);
                                }
                            },
                            complete:function(){
                                canPost = true;
                                secondBtn.text("充值");
                            }
                        })
                    }
                }else{
                    return org.ui.alert('充值中，请稍后');
                }
            })
        }
    }
    return {
        init : lib.init
    }
})(org);

org.authentication = (function(org){
    var lib = {
        isPost: true,
        $fromComplete : $(".from-four-complete"),
        init: function(){
            lib._checkForm();
        },
        _checkForm :function(){
            var formName = ['name','id_number'],
                formError = ['.error-name', '.error-card'],
                formSign = ['请输入姓名', '请输入身份证号', '请输入有效身份证'],
                data = {},
                reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/; //身份证正则

            lib.$fromComplete.on('click',function(){
                var isFor = true;
                $('.sign-all').hide();
                $('.check-input').each(function(i){
                    if(!$(this).val()){
                        isFor =false;
                        return $(formError[i]).text(formSign[i]).show();
                    }else{
                        if(i === 1 && !reg.test($(this).val())){
                            isFor =false;
                            return $(formError[i]).text(formSign[2]).show();
                        }
                    }
                    data[formName[i]] = $(this).val();
                })
                isFor && lib._forAuthentication(data)
            });
        },
        _forAuthentication:function(ags){
            if(lib.isPost){
                org.ajax({
                    type: 'POST',
                    url : '/api/id_validate/',
                    data : ags,
                    beforeSend:function(){
                        lib.isPost = false;
                        lib.$fromComplete.text("认证中，请等待...");
                    },
                    success:function(){
                        org.ui.alert("实名认证成功!",function(){
                           return window.location.href = '/weixin/security/';
                        });
                    },
                    error:function(xhr){
                        result = JSON.parse(xhr.responseText);
                        return org.ui.alert(result.message);
                    },
                    complete:function(){
                        lib.isPost = true;
                        lib.$fromComplete.text("完成");
                    }
                })
            }
        }
    };
    return {
        init :lib.init
    }
})(org);

org.bankcardAdd = (function(org){
    var lib = {
        init:function(){
            lib._checkForm();
        },
        _checkForm:function(){
            var reg = /^\d{10,20}$/;
            $(".addBank-btn").on('click',function(){
                var gate_id = $('#bank-select').val(),
                    card_number = $('#card-no').val(),
                    is_default = $('#default-checkbox').prop('checked');

                if (!gate_id) {
                    return org.ui.alert('请选择银行');
                }
                if(!reg.test(card_number)){
                    return org.ui.alert('请输入有效的银行卡号')
                }
                var data =  {
                  card_number: card_number,
                  gate_id : gate_id,
                  is_default : is_default
                }

                lib._forAddbank(data);
            });
        },
        _forAddbank:function(data){
            org.ajax({
                type: "POST",
                url: '/api/bank_card/add/',
                data: data,
                beforeSend:function(){
                   $(".addBank-btn").attr("disabled","true").text("添加中...");
                },
                success:function(result){
                    if(result.ret_code === 0){
                        org.ui.alert("添加成功！",function(){
                             window.location.href = '/weixin/account/bankcard/';
                        });
                    }else if(result.ret_code > 0){
                        org.ui.alert(result.message);
                    }
                },
                error:function(result){
                    if (result.error_number === 6) {
                      return org.ui.alert(result.message);
                    }else{
                        return org.ui.alert("添加银行卡失败");
                    }
                },
                complete:function(){
                    $(".addBank-btn").removeAttr("disabled").text("添加银行卡");
                }

            })
        }
    }
    return {
        init : lib.init
    }
})(org);

org.anniversary = (function(org){
    var lib = {
        init:function(){
            $('.bannerFonts').addClass('bannerFontsHover');
        }
    }
    return {
        init : lib.init
    }
})(org);


;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if(src && src.indexOf(org.scriptName) > 0){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);
