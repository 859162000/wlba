/* Zepto v1.1.6 - zepto event ajax form ie - zeptojs.com/license */
var Zepto=function(){function L(t){return null==t?String(t):j[S.call(t)]||"object"}function Z(t){return"function"==L(t)}function _(t){return null!=t&&t==t.window}function $(t){return null!=t&&t.nodeType==t.DOCUMENT_NODE}function D(t){return"object"==L(t)}function M(t){return D(t)&&!_(t)&&Object.getPrototypeOf(t)==Object.prototype}function R(t){return"number"==typeof t.length}function k(t){return s.call(t,function(t){return null!=t})}function z(t){return t.length>0?n.fn.concat.apply([],t):t}function F(t){return t.replace(/::/g,"/").replace(/([A-Z]+)([A-Z][a-z])/g,"$1_$2").replace(/([a-z\d])([A-Z])/g,"$1_$2").replace(/_/g,"-").toLowerCase()}function q(t){return t in f?f[t]:f[t]=new RegExp("(^|\\s)"+t+"(\\s|$)")}function H(t,e){return"number"!=typeof e||c[F(t)]?e:e+"px"}function I(t){var e,n;return u[t]||(e=a.createElement(t),a.body.appendChild(e),n=getComputedStyle(e,"").getPropertyValue("display"),e.parentNode.removeChild(e),"none"==n&&(n="block"),u[t]=n),u[t]}function V(t){return"children"in t?o.call(t.children):n.map(t.childNodes,function(t){return 1==t.nodeType?t:void 0})}function B(n,i,r){for(e in i)r&&(M(i[e])||A(i[e]))?(M(i[e])&&!M(n[e])&&(n[e]={}),A(i[e])&&!A(n[e])&&(n[e]=[]),B(n[e],i[e],r)):i[e]!==t&&(n[e]=i[e])}function U(t,e){return null==e?n(t):n(t).filter(e)}function J(t,e,n,i){return Z(e)?e.call(t,n,i):e}function X(t,e,n){null==n?t.removeAttribute(e):t.setAttribute(e,n)}function W(e,n){var i=e.className||"",r=i&&i.baseVal!==t;return n===t?r?i.baseVal:i:void(r?i.baseVal=n:e.className=n)}function Y(t){try{return t?"true"==t||("false"==t?!1:"null"==t?null:+t+""==t?+t:/^[\[\{]/.test(t)?n.parseJSON(t):t):t}catch(e){return t}}function G(t,e){e(t);for(var n=0,i=t.childNodes.length;i>n;n++)G(t.childNodes[n],e)}var t,e,n,i,C,N,r=[],o=r.slice,s=r.filter,a=window.document,u={},f={},c={"column-count":1,columns:1,"font-weight":1,"line-height":1,opacity:1,"z-index":1,zoom:1},l=/^\s*<(\w+|!)[^>]*>/,h=/^<(\w+)\s*\/?>(?:<\/\1>|)$/,p=/<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/gi,d=/^(?:body|html)$/i,m=/([A-Z])/g,g=["val","css","html","text","data","width","height","offset"],v=["after","prepend","before","append"],y=a.createElement("table"),x=a.createElement("tr"),b={tr:a.createElement("tbody"),tbody:y,thead:y,tfoot:y,td:x,th:x,"*":a.createElement("div")},w=/complete|loaded|interactive/,E=/^[\w-]*$/,j={},S=j.toString,T={},O=a.createElement("div"),P={tabindex:"tabIndex",readonly:"readOnly","for":"htmlFor","class":"className",maxlength:"maxLength",cellspacing:"cellSpacing",cellpadding:"cellPadding",rowspan:"rowSpan",colspan:"colSpan",usemap:"useMap",frameborder:"frameBorder",contenteditable:"contentEditable"},A=Array.isArray||function(t){return t instanceof Array};return T.matches=function(t,e){if(!e||!t||1!==t.nodeType)return!1;var n=t.webkitMatchesSelector||t.mozMatchesSelector||t.oMatchesSelector||t.matchesSelector;if(n)return n.call(t,e);var i,r=t.parentNode,o=!r;return o&&(r=O).appendChild(t),i=~T.qsa(r,e).indexOf(t),o&&O.removeChild(t),i},C=function(t){return t.replace(/-+(.)?/g,function(t,e){return e?e.toUpperCase():""})},N=function(t){return s.call(t,function(e,n){return t.indexOf(e)==n})},T.fragment=function(e,i,r){var s,u,f;return h.test(e)&&(s=n(a.createElement(RegExp.$1))),s||(e.replace&&(e=e.replace(p,"<$1></$2>")),i===t&&(i=l.test(e)&&RegExp.$1),i in b||(i="*"),f=b[i],f.innerHTML=""+e,s=n.each(o.call(f.childNodes),function(){f.removeChild(this)})),M(r)&&(u=n(s),n.each(r,function(t,e){g.indexOf(t)>-1?u[t](e):u.attr(t,e)})),s},T.Z=function(t,e){return t=t||[],t.__proto__=n.fn,t.selector=e||"",t},T.isZ=function(t){return t instanceof T.Z},T.init=function(e,i){var r;if(!e)return T.Z();if("string"==typeof e)if(e=e.trim(),"<"==e[0]&&l.test(e))r=T.fragment(e,RegExp.$1,i),e=null;else{if(i!==t)return n(i).find(e);r=T.qsa(a,e)}else{if(Z(e))return n(a).ready(e);if(T.isZ(e))return e;if(A(e))r=k(e);else if(D(e))r=[e],e=null;else if(l.test(e))r=T.fragment(e.trim(),RegExp.$1,i),e=null;else{if(i!==t)return n(i).find(e);r=T.qsa(a,e)}}return T.Z(r,e)},n=function(t,e){return T.init(t,e)},n.extend=function(t){var e,n=o.call(arguments,1);return"boolean"==typeof t&&(e=t,t=n.shift()),n.forEach(function(n){B(t,n,e)}),t},T.qsa=function(t,e){var n,i="#"==e[0],r=!i&&"."==e[0],s=i||r?e.slice(1):e,a=E.test(s);return $(t)&&a&&i?(n=t.getElementById(s))?[n]:[]:1!==t.nodeType&&9!==t.nodeType?[]:o.call(a&&!i?r?t.getElementsByClassName(s):t.getElementsByTagName(e):t.querySelectorAll(e))},n.contains=a.documentElement.contains?function(t,e){return t!==e&&t.contains(e)}:function(t,e){for(;e&&(e=e.parentNode);)if(e===t)return!0;return!1},n.type=L,n.isFunction=Z,n.isWindow=_,n.isArray=A,n.isPlainObject=M,n.isEmptyObject=function(t){var e;for(e in t)return!1;return!0},n.inArray=function(t,e,n){return r.indexOf.call(e,t,n)},n.camelCase=C,n.trim=function(t){return null==t?"":String.prototype.trim.call(t)},n.uuid=0,n.support={},n.expr={},n.map=function(t,e){var n,r,o,i=[];if(R(t))for(r=0;r<t.length;r++)n=e(t[r],r),null!=n&&i.push(n);else for(o in t)n=e(t[o],o),null!=n&&i.push(n);return z(i)},n.each=function(t,e){var n,i;if(R(t)){for(n=0;n<t.length;n++)if(e.call(t[n],n,t[n])===!1)return t}else for(i in t)if(e.call(t[i],i,t[i])===!1)return t;return t},n.grep=function(t,e){return s.call(t,e)},window.JSON&&(n.parseJSON=JSON.parse),n.each("Boolean Number String Function Array Date RegExp Object Error".split(" "),function(t,e){j["[object "+e+"]"]=e.toLowerCase()}),n.fn={forEach:r.forEach,reduce:r.reduce,push:r.push,sort:r.sort,indexOf:r.indexOf,concat:r.concat,map:function(t){return n(n.map(this,function(e,n){return t.call(e,n,e)}))},slice:function(){return n(o.apply(this,arguments))},ready:function(t){return w.test(a.readyState)&&a.body?t(n):a.addEventListener("DOMContentLoaded",function(){t(n)},!1),this},get:function(e){return e===t?o.call(this):this[e>=0?e:e+this.length]},toArray:function(){return this.get()},size:function(){return this.length},remove:function(){return this.each(function(){null!=this.parentNode&&this.parentNode.removeChild(this)})},each:function(t){return r.every.call(this,function(e,n){return t.call(e,n,e)!==!1}),this},filter:function(t){return Z(t)?this.not(this.not(t)):n(s.call(this,function(e){return T.matches(e,t)}))},add:function(t,e){return n(N(this.concat(n(t,e))))},is:function(t){return this.length>0&&T.matches(this[0],t)},not:function(e){var i=[];if(Z(e)&&e.call!==t)this.each(function(t){e.call(this,t)||i.push(this)});else{var r="string"==typeof e?this.filter(e):R(e)&&Z(e.item)?o.call(e):n(e);this.forEach(function(t){r.indexOf(t)<0&&i.push(t)})}return n(i)},has:function(t){return this.filter(function(){return D(t)?n.contains(this,t):n(this).find(t).size()})},eq:function(t){return-1===t?this.slice(t):this.slice(t,+t+1)},first:function(){var t=this[0];return t&&!D(t)?t:n(t)},last:function(){var t=this[this.length-1];return t&&!D(t)?t:n(t)},find:function(t){var e,i=this;return e=t?"object"==typeof t?n(t).filter(function(){var t=this;return r.some.call(i,function(e){return n.contains(e,t)})}):1==this.length?n(T.qsa(this[0],t)):this.map(function(){return T.qsa(this,t)}):n()},closest:function(t,e){var i=this[0],r=!1;for("object"==typeof t&&(r=n(t));i&&!(r?r.indexOf(i)>=0:T.matches(i,t));)i=i!==e&&!$(i)&&i.parentNode;return n(i)},parents:function(t){for(var e=[],i=this;i.length>0;)i=n.map(i,function(t){return(t=t.parentNode)&&!$(t)&&e.indexOf(t)<0?(e.push(t),t):void 0});return U(e,t)},parent:function(t){return U(N(this.pluck("parentNode")),t)},children:function(t){return U(this.map(function(){return V(this)}),t)},contents:function(){return this.map(function(){return o.call(this.childNodes)})},siblings:function(t){return U(this.map(function(t,e){return s.call(V(e.parentNode),function(t){return t!==e})}),t)},empty:function(){return this.each(function(){this.innerHTML=""})},pluck:function(t){return n.map(this,function(e){return e[t]})},show:function(){return this.each(function(){"none"==this.style.display&&(this.style.display=""),"none"==getComputedStyle(this,"").getPropertyValue("display")&&(this.style.display=I(this.nodeName))})},replaceWith:function(t){return this.before(t).remove()},wrap:function(t){var e=Z(t);if(this[0]&&!e)var i=n(t).get(0),r=i.parentNode||this.length>1;return this.each(function(o){n(this).wrapAll(e?t.call(this,o):r?i.cloneNode(!0):i)})},wrapAll:function(t){if(this[0]){n(this[0]).before(t=n(t));for(var e;(e=t.children()).length;)t=e.first();n(t).append(this)}return this},wrapInner:function(t){var e=Z(t);return this.each(function(i){var r=n(this),o=r.contents(),s=e?t.call(this,i):t;o.length?o.wrapAll(s):r.append(s)})},unwrap:function(){return this.parent().each(function(){n(this).replaceWith(n(this).children())}),this},clone:function(){return this.map(function(){return this.cloneNode(!0)})},hide:function(){return this.css("display","none")},toggle:function(e){return this.each(function(){var i=n(this);(e===t?"none"==i.css("display"):e)?i.show():i.hide()})},prev:function(t){return n(this.pluck("previousElementSibling")).filter(t||"*")},next:function(t){return n(this.pluck("nextElementSibling")).filter(t||"*")},html:function(t){return 0 in arguments?this.each(function(e){var i=this.innerHTML;n(this).empty().append(J(this,t,e,i))}):0 in this?this[0].innerHTML:null},text:function(t){return 0 in arguments?this.each(function(e){var n=J(this,t,e,this.textContent);this.textContent=null==n?"":""+n}):0 in this?this[0].textContent:null},attr:function(n,i){var r;return"string"!=typeof n||1 in arguments?this.each(function(t){if(1===this.nodeType)if(D(n))for(e in n)X(this,e,n[e]);else X(this,n,J(this,i,t,this.getAttribute(n)))}):this.length&&1===this[0].nodeType?!(r=this[0].getAttribute(n))&&n in this[0]?this[0][n]:r:t},removeAttr:function(t){return this.each(function(){1===this.nodeType&&t.split(" ").forEach(function(t){X(this,t)},this)})},prop:function(t,e){return t=P[t]||t,1 in arguments?this.each(function(n){this[t]=J(this,e,n,this[t])}):this[0]&&this[0][t]},data:function(e,n){var i="data-"+e.replace(m,"-$1").toLowerCase(),r=1 in arguments?this.attr(i,n):this.attr(i);return null!==r?Y(r):t},val:function(t){return 0 in arguments?this.each(function(e){this.value=J(this,t,e,this.value)}):this[0]&&(this[0].multiple?n(this[0]).find("option").filter(function(){return this.selected}).pluck("value"):this[0].value)},offset:function(t){if(t)return this.each(function(e){var i=n(this),r=J(this,t,e,i.offset()),o=i.offsetParent().offset(),s={top:r.top-o.top,left:r.left-o.left};"static"==i.css("position")&&(s.position="relative"),i.css(s)});if(!this.length)return null;var e=this[0].getBoundingClientRect();return{left:e.left+window.pageXOffset,top:e.top+window.pageYOffset,width:Math.round(e.width),height:Math.round(e.height)}},css:function(t,i){if(arguments.length<2){var r,o=this[0];if(!o)return;if(r=getComputedStyle(o,""),"string"==typeof t)return o.style[C(t)]||r.getPropertyValue(t);if(A(t)){var s={};return n.each(t,function(t,e){s[e]=o.style[C(e)]||r.getPropertyValue(e)}),s}}var a="";if("string"==L(t))i||0===i?a=F(t)+":"+H(t,i):this.each(function(){this.style.removeProperty(F(t))});else for(e in t)t[e]||0===t[e]?a+=F(e)+":"+H(e,t[e])+";":this.each(function(){this.style.removeProperty(F(e))});return this.each(function(){this.style.cssText+=";"+a})},index:function(t){return t?this.indexOf(n(t)[0]):this.parent().children().indexOf(this[0])},hasClass:function(t){return t?r.some.call(this,function(t){return this.test(W(t))},q(t)):!1},addClass:function(t){return t?this.each(function(e){if("className"in this){i=[];var r=W(this),o=J(this,t,e,r);o.split(/\s+/g).forEach(function(t){n(this).hasClass(t)||i.push(t)},this),i.length&&W(this,r+(r?" ":"")+i.join(" "))}}):this},removeClass:function(e){return this.each(function(n){if("className"in this){if(e===t)return W(this,"");i=W(this),J(this,e,n,i).split(/\s+/g).forEach(function(t){i=i.replace(q(t)," ")}),W(this,i.trim())}})},toggleClass:function(e,i){return e?this.each(function(r){var o=n(this),s=J(this,e,r,W(this));s.split(/\s+/g).forEach(function(e){(i===t?!o.hasClass(e):i)?o.addClass(e):o.removeClass(e)})}):this},scrollTop:function(e){if(this.length){var n="scrollTop"in this[0];return e===t?n?this[0].scrollTop:this[0].pageYOffset:this.each(n?function(){this.scrollTop=e}:function(){this.scrollTo(this.scrollX,e)})}},scrollLeft:function(e){if(this.length){var n="scrollLeft"in this[0];return e===t?n?this[0].scrollLeft:this[0].pageXOffset:this.each(n?function(){this.scrollLeft=e}:function(){this.scrollTo(e,this.scrollY)})}},position:function(){if(this.length){var t=this[0],e=this.offsetParent(),i=this.offset(),r=d.test(e[0].nodeName)?{top:0,left:0}:e.offset();return i.top-=parseFloat(n(t).css("margin-top"))||0,i.left-=parseFloat(n(t).css("margin-left"))||0,r.top+=parseFloat(n(e[0]).css("border-top-width"))||0,r.left+=parseFloat(n(e[0]).css("border-left-width"))||0,{top:i.top-r.top,left:i.left-r.left}}},offsetParent:function(){return this.map(function(){for(var t=this.offsetParent||a.body;t&&!d.test(t.nodeName)&&"static"==n(t).css("position");)t=t.offsetParent;return t})}},n.fn.detach=n.fn.remove,["width","height"].forEach(function(e){var i=e.replace(/./,function(t){return t[0].toUpperCase()});n.fn[e]=function(r){var o,s=this[0];return r===t?_(s)?s["inner"+i]:$(s)?s.documentElement["scroll"+i]:(o=this.offset())&&o[e]:this.each(function(t){s=n(this),s.css(e,J(this,r,t,s[e]()))})}}),v.forEach(function(t,e){var i=e%2;n.fn[t]=function(){var t,o,r=n.map(arguments,function(e){return t=L(e),"object"==t||"array"==t||null==e?e:T.fragment(e)}),s=this.length>1;return r.length<1?this:this.each(function(t,u){o=i?u:u.parentNode,u=0==e?u.nextSibling:1==e?u.firstChild:2==e?u:null;var f=n.contains(a.documentElement,o);r.forEach(function(t){if(s)t=t.cloneNode(!0);else if(!o)return n(t).remove();o.insertBefore(t,u),f&&G(t,function(t){null==t.nodeName||"SCRIPT"!==t.nodeName.toUpperCase()||t.type&&"text/javascript"!==t.type||t.src||window.eval.call(window,t.innerHTML)})})})},n.fn[i?t+"To":"insert"+(e?"Before":"After")]=function(e){return n(e)[t](this),this}}),T.Z.prototype=n.fn,T.uniq=N,T.deserializeValue=Y,n.zepto=T,n}();window.Zepto=Zepto,void 0===window.$&&(window.$=Zepto),function(t){function l(t){return t._zid||(t._zid=e++)}function h(t,e,n,i){if(e=p(e),e.ns)var r=d(e.ns);return(s[l(t)]||[]).filter(function(t){return!(!t||e.e&&t.e!=e.e||e.ns&&!r.test(t.ns)||n&&l(t.fn)!==l(n)||i&&t.sel!=i)})}function p(t){var e=(""+t).split(".");return{e:e[0],ns:e.slice(1).sort().join(" ")}}function d(t){return new RegExp("(?:^| )"+t.replace(" "," .* ?")+"(?: |$)")}function m(t,e){return t.del&&!u&&t.e in f||!!e}function g(t){return c[t]||u&&f[t]||t}function v(e,i,r,o,a,u,f){var h=l(e),d=s[h]||(s[h]=[]);i.split(/\s/).forEach(function(i){if("ready"==i)return t(document).ready(r);var s=p(i);s.fn=r,s.sel=a,s.e in c&&(r=function(e){var n=e.relatedTarget;return!n||n!==this&&!t.contains(this,n)?s.fn.apply(this,arguments):void 0}),s.del=u;var l=u||r;s.proxy=function(t){if(t=j(t),!t.isImmediatePropagationStopped()){t.data=o;var i=l.apply(e,t._args==n?[t]:[t].concat(t._args));return i===!1&&(t.preventDefault(),t.stopPropagation()),i}},s.i=d.length,d.push(s),"addEventListener"in e&&e.addEventListener(g(s.e),s.proxy,m(s,f))})}function y(t,e,n,i,r){var o=l(t);(e||"").split(/\s/).forEach(function(e){h(t,e,n,i).forEach(function(e){delete s[o][e.i],"removeEventListener"in t&&t.removeEventListener(g(e.e),e.proxy,m(e,r))})})}function j(e,i){return(i||!e.isDefaultPrevented)&&(i||(i=e),t.each(E,function(t,n){var r=i[t];e[t]=function(){return this[n]=x,r&&r.apply(i,arguments)},e[n]=b}),(i.defaultPrevented!==n?i.defaultPrevented:"returnValue"in i?i.returnValue===!1:i.getPreventDefault&&i.getPreventDefault())&&(e.isDefaultPrevented=x)),e}function S(t){var e,i={originalEvent:t};for(e in t)w.test(e)||t[e]===n||(i[e]=t[e]);return j(i,t)}var n,e=1,i=Array.prototype.slice,r=t.isFunction,o=function(t){return"string"==typeof t},s={},a={},u="onfocusin"in window,f={focus:"focusin",blur:"focusout"},c={mouseenter:"mouseover",mouseleave:"mouseout"};a.click=a.mousedown=a.mouseup=a.mousemove="MouseEvents",t.event={add:v,remove:y},t.proxy=function(e,n){var s=2 in arguments&&i.call(arguments,2);if(r(e)){var a=function(){return e.apply(n,s?s.concat(i.call(arguments)):arguments)};return a._zid=l(e),a}if(o(n))return s?(s.unshift(e[n],e),t.proxy.apply(null,s)):t.proxy(e[n],e);throw new TypeError("expected function")},t.fn.bind=function(t,e,n){return this.on(t,e,n)},t.fn.unbind=function(t,e){return this.off(t,e)},t.fn.one=function(t,e,n,i){return this.on(t,e,n,i,1)};var x=function(){return!0},b=function(){return!1},w=/^([A-Z]|returnValue$|layer[XY]$)/,E={preventDefault:"isDefaultPrevented",stopImmediatePropagation:"isImmediatePropagationStopped",stopPropagation:"isPropagationStopped"};t.fn.delegate=function(t,e,n){return this.on(e,t,n)},t.fn.undelegate=function(t,e,n){return this.off(e,t,n)},t.fn.live=function(e,n){return t(document.body).delegate(this.selector,e,n),this},t.fn.die=function(e,n){return t(document.body).undelegate(this.selector,e,n),this},t.fn.on=function(e,s,a,u,f){var c,l,h=this;return e&&!o(e)?(t.each(e,function(t,e){h.on(t,s,a,e,f)}),h):(o(s)||r(u)||u===!1||(u=a,a=s,s=n),(r(a)||a===!1)&&(u=a,a=n),u===!1&&(u=b),h.each(function(n,r){f&&(c=function(t){return y(r,t.type,u),u.apply(this,arguments)}),s&&(l=function(e){var n,o=t(e.target).closest(s,r).get(0);return o&&o!==r?(n=t.extend(S(e),{currentTarget:o,liveFired:r}),(c||u).apply(o,[n].concat(i.call(arguments,1)))):void 0}),v(r,e,u,a,s,l||c)}))},t.fn.off=function(e,i,s){var a=this;return e&&!o(e)?(t.each(e,function(t,e){a.off(t,i,e)}),a):(o(i)||r(s)||s===!1||(s=i,i=n),s===!1&&(s=b),a.each(function(){y(this,e,s,i)}))},t.fn.trigger=function(e,n){return e=o(e)||t.isPlainObject(e)?t.Event(e):j(e),e._args=n,this.each(function(){e.type in f&&"function"==typeof this[e.type]?this[e.type]():"dispatchEvent"in this?this.dispatchEvent(e):t(this).triggerHandler(e,n)})},t.fn.triggerHandler=function(e,n){var i,r;return this.each(function(s,a){i=S(o(e)?t.Event(e):e),i._args=n,i.target=a,t.each(h(a,e.type||e),function(t,e){return r=e.proxy(i),i.isImmediatePropagationStopped()?!1:void 0})}),r},"focusin focusout focus blur load resize scroll unload click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select keydown keypress keyup error".split(" ").forEach(function(e){t.fn[e]=function(t){return 0 in arguments?this.bind(e,t):this.trigger(e)}}),t.Event=function(t,e){o(t)||(e=t,t=e.type);var n=document.createEvent(a[t]||"Events"),i=!0;if(e)for(var r in e)"bubbles"==r?i=!!e[r]:n[r]=e[r];return n.initEvent(t,i,!0),j(n)}}(Zepto),function(t){function h(e,n,i){var r=t.Event(n);return t(e).trigger(r,i),!r.isDefaultPrevented()}function p(t,e,i,r){return t.global?h(e||n,i,r):void 0}function d(e){e.global&&0===t.active++&&p(e,null,"ajaxStart")}function m(e){e.global&&!--t.active&&p(e,null,"ajaxStop")}function g(t,e){var n=e.context;return e.beforeSend.call(n,t,e)===!1||p(e,n,"ajaxBeforeSend",[t,e])===!1?!1:void p(e,n,"ajaxSend",[t,e])}function v(t,e,n,i){var r=n.context,o="success";n.success.call(r,t,o,e),i&&i.resolveWith(r,[t,o,e]),p(n,r,"ajaxSuccess",[e,n,t]),x(o,e,n)}function y(t,e,n,i,r){var o=i.context;i.error.call(o,n,e,t),r&&r.rejectWith(o,[n,e,t]),p(i,o,"ajaxError",[n,i,t||e]),x(e,n,i)}function x(t,e,n){var i=n.context;n.complete.call(i,e,t),p(n,i,"ajaxComplete",[e,n]),m(n)}function b(){}function w(t){return t&&(t=t.split(";",2)[0]),t&&(t==f?"html":t==u?"json":s.test(t)?"script":a.test(t)&&"xml")||"text"}function E(t,e){return""==e?t:(t+"&"+e).replace(/[&?]{1,2}/,"?")}function j(e){e.processData&&e.data&&"string"!=t.type(e.data)&&(e.data=t.param(e.data,e.traditional)),!e.data||e.type&&"GET"!=e.type.toUpperCase()||(e.url=E(e.url,e.data),e.data=void 0)}function S(e,n,i,r){return t.isFunction(n)&&(r=i,i=n,n=void 0),t.isFunction(i)||(r=i,i=void 0),{url:e,data:n,success:i,dataType:r}}function C(e,n,i,r){var o,s=t.isArray(n),a=t.isPlainObject(n);t.each(n,function(n,u){o=t.type(u),r&&(n=i?r:r+"["+(a||"object"==o||"array"==o?n:"")+"]"),!r&&s?e.add(u.name,u.value):"array"==o||!i&&"object"==o?C(e,u,i,n):e.add(n,u)})}var i,r,e=0,n=window.document,o=/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,s=/^(?:text|application)\/javascript/i,a=/^(?:text|application)\/xml/i,u="application/json",f="text/html",c=/^\s*$/,l=n.createElement("a");l.href=window.location.href,t.active=0,t.ajaxJSONP=function(i,r){if(!("type"in i))return t.ajax(i);var f,h,o=i.jsonpCallback,s=(t.isFunction(o)?o():o)||"jsonp"+ ++e,a=n.createElement("script"),u=window[s],c=function(e){t(a).triggerHandler("error",e||"abort")},l={abort:c};return r&&r.promise(l),t(a).on("load error",function(e,n){clearTimeout(h),t(a).off().remove(),"error"!=e.type&&f?v(f[0],l,i,r):y(null,n||"error",l,i,r),window[s]=u,f&&t.isFunction(u)&&u(f[0]),u=f=void 0}),g(l,i)===!1?(c("abort"),l):(window[s]=function(){f=arguments},a.src=i.url.replace(/\?(.+)=\?/,"?$1="+s),n.head.appendChild(a),i.timeout>0&&(h=setTimeout(function(){c("timeout")},i.timeout)),l)},t.ajaxSettings={type:"GET",beforeSend:b,success:b,error:b,complete:b,context:null,global:!0,xhr:function(){return new window.XMLHttpRequest},accepts:{script:"text/javascript, application/javascript, application/x-javascript",json:u,xml:"application/xml, text/xml",html:f,text:"text/plain"},crossDomain:!1,timeout:0,processData:!0,cache:!0},t.ajax=function(e){var a,o=t.extend({},e||{}),s=t.Deferred&&t.Deferred();for(i in t.ajaxSettings)void 0===o[i]&&(o[i]=t.ajaxSettings[i]);d(o),o.crossDomain||(a=n.createElement("a"),a.href=o.url,a.href=a.href,o.crossDomain=l.protocol+"//"+l.host!=a.protocol+"//"+a.host),o.url||(o.url=window.location.toString()),j(o);var u=o.dataType,f=/\?.+=\?/.test(o.url);if(f&&(u="jsonp"),o.cache!==!1&&(e&&e.cache===!0||"script"!=u&&"jsonp"!=u)||(o.url=E(o.url,"_="+Date.now())),"jsonp"==u)return f||(o.url=E(o.url,o.jsonp?o.jsonp+"=?":o.jsonp===!1?"":"callback=?")),t.ajaxJSONP(o,s);var C,h=o.accepts[u],p={},m=function(t,e){p[t.toLowerCase()]=[t,e]},x=/^([\w-]+:)\/\//.test(o.url)?RegExp.$1:window.location.protocol,S=o.xhr(),T=S.setRequestHeader;if(s&&s.promise(S),o.crossDomain||m("X-Requested-With","XMLHttpRequest"),m("Accept",h||"*/*"),(h=o.mimeType||h)&&(h.indexOf(",")>-1&&(h=h.split(",",2)[0]),S.overrideMimeType&&S.overrideMimeType(h)),(o.contentType||o.contentType!==!1&&o.data&&"GET"!=o.type.toUpperCase())&&m("Content-Type",o.contentType||"application/x-www-form-urlencoded"),o.headers)for(r in o.headers)m(r,o.headers[r]);if(S.setRequestHeader=m,S.onreadystatechange=function(){if(4==S.readyState){S.onreadystatechange=b,clearTimeout(C);var e,n=!1;if(S.status>=200&&S.status<300||304==S.status||0==S.status&&"file:"==x){u=u||w(o.mimeType||S.getResponseHeader("content-type")),e=S.responseText;try{"script"==u?(1,eval)(e):"xml"==u?e=S.responseXML:"json"==u&&(e=c.test(e)?null:t.parseJSON(e))}catch(i){n=i}n?y(n,"parsererror",S,o,s):v(e,S,o,s)}else y(S.statusText||null,S.status?"error":"abort",S,o,s)}},g(S,o)===!1)return S.abort(),y(null,"abort",S,o,s),S;if(o.xhrFields)for(r in o.xhrFields)S[r]=o.xhrFields[r];var N="async"in o?o.async:!0;S.open(o.type,o.url,N,o.username,o.password);for(r in p)T.apply(S,p[r]);return o.timeout>0&&(C=setTimeout(function(){S.onreadystatechange=b,S.abort(),y(null,"timeout",S,o,s)},o.timeout)),S.send(o.data?o.data:null),S},t.get=function(){return t.ajax(S.apply(null,arguments))},t.post=function(){var e=S.apply(null,arguments);return e.type="POST",t.ajax(e)},t.getJSON=function(){var e=S.apply(null,arguments);return e.dataType="json",t.ajax(e)},t.fn.load=function(e,n,i){if(!this.length)return this;var a,r=this,s=e.split(/\s/),u=S(e,n,i),f=u.success;return s.length>1&&(u.url=s[0],a=s[1]),u.success=function(e){r.html(a?t("<div>").html(e.replace(o,"")).find(a):e),f&&f.apply(r,arguments)},t.ajax(u),this};var T=encodeURIComponent;t.param=function(e,n){var i=[];return i.add=function(e,n){t.isFunction(n)&&(n=n()),null==n&&(n=""),this.push(T(e)+"="+T(n))},C(i,e,n),i.join("&").replace(/%20/g,"+")}}(Zepto),function(t){t.fn.serializeArray=function(){var e,n,i=[],r=function(t){return t.forEach?t.forEach(r):void i.push({name:e,value:t})};return this[0]&&t.each(this[0].elements,function(i,o){n=o.type,e=o.name,e&&"fieldset"!=o.nodeName.toLowerCase()&&!o.disabled&&"submit"!=n&&"reset"!=n&&"button"!=n&&"file"!=n&&("radio"!=n&&"checkbox"!=n||o.checked)&&r(t(o).val())}),i},t.fn.serialize=function(){var t=[];return this.serializeArray().forEach(function(e){t.push(encodeURIComponent(e.name)+"="+encodeURIComponent(e.value))}),t.join("&")},t.fn.submit=function(e){if(0 in arguments)this.bind("submit",e);else if(this.length){var n=t.Event("submit");this.eq(0).trigger(n),n.isDefaultPrevented()||this.get(0).submit()}return this}}(Zepto),function(t){"__proto__"in{}||t.extend(t.zepto,{Z:function(e,n){return e=e||[],t.extend(e,t.fn),e.selector=n||"",e.__Z=!0,e},isZ:function(e){return"array"===t.type(e)&&"__Z"in e}});try{getComputedStyle(void 0)}catch(e){var n=getComputedStyle;window.getComputedStyle=function(t){try{return n(t)}catch(e){return null}}}}(Zepto);
//     Zepto.js
//     (c) 2010-2016 Thomas Fuchs
//     Zepto.js may be freely distributed under the MIT license.

;(function($, undefined){
  var prefix = '', eventPrefix,
    vendors = { Webkit: 'webkit', Moz: '', O: 'o' },
    testEl = document.createElement('div'),
    supportedTransforms = /^((translate|rotate|scale)(X|Y|Z|3d)?|matrix(3d)?|perspective|skew(X|Y)?)$/i,
    transform,
    transitionProperty, transitionDuration, transitionTiming, transitionDelay,
    animationName, animationDuration, animationTiming, animationDelay,
    cssReset = {}

  function dasherize(str) { return str.replace(/([a-z])([A-Z])/, '$1-$2').toLowerCase() }
  function normalizeEvent(name) { return eventPrefix ? eventPrefix + name : name.toLowerCase() }

  $.each(vendors, function(vendor, event){
    if (testEl.style[vendor + 'TransitionProperty'] !== undefined) {
      prefix = '-' + vendor.toLowerCase() + '-'
      eventPrefix = event
      return false
    }
  })

  transform = prefix + 'transform'
  cssReset[transitionProperty = prefix + 'transition-property'] =
  cssReset[transitionDuration = prefix + 'transition-duration'] =
  cssReset[transitionDelay    = prefix + 'transition-delay'] =
  cssReset[transitionTiming   = prefix + 'transition-timing-function'] =
  cssReset[animationName      = prefix + 'animation-name'] =
  cssReset[animationDuration  = prefix + 'animation-duration'] =
  cssReset[animationDelay     = prefix + 'animation-delay'] =
  cssReset[animationTiming    = prefix + 'animation-timing-function'] = ''

  $.fx = {
    off: (eventPrefix === undefined && testEl.style.transitionProperty === undefined),
    speeds: { _default: 400, fast: 200, slow: 600 },
    cssPrefix: prefix,
    transitionEnd: normalizeEvent('TransitionEnd'),
    animationEnd: normalizeEvent('AnimationEnd')
  }

  $.fn.animate = function(properties, duration, ease, callback, delay){
    if ($.isFunction(duration))
      callback = duration, ease = undefined, duration = undefined
    if ($.isFunction(ease))
      callback = ease, ease = undefined
    if ($.isPlainObject(duration))
      ease = duration.easing, callback = duration.complete, delay = duration.delay, duration = duration.duration
    if (duration) duration = (typeof duration == 'number' ? duration :
                    ($.fx.speeds[duration] || $.fx.speeds._default)) / 1000
    if (delay) delay = parseFloat(delay) / 1000
    return this.anim(properties, duration, ease, callback, delay)
  }

  $.fn.anim = function(properties, duration, ease, callback, delay){
    var key, cssValues = {}, cssProperties, transforms = '',
        that = this, wrappedCallback, endEvent = $.fx.transitionEnd,
        fired = false

    if (duration === undefined) duration = $.fx.speeds._default / 1000
    if (delay === undefined) delay = 0
    if ($.fx.off) duration = 0

    if (typeof properties == 'string') {
      // keyframe animation
      cssValues[animationName] = properties
      cssValues[animationDuration] = duration + 's'
      cssValues[animationDelay] = delay + 's'
      cssValues[animationTiming] = (ease || 'linear')
      endEvent = $.fx.animationEnd
    } else {
      cssProperties = []
      // CSS transitions
      for (key in properties)
        if (supportedTransforms.test(key)) transforms += key + '(' + properties[key] + ') '
        else cssValues[key] = properties[key], cssProperties.push(dasherize(key))

      if (transforms) cssValues[transform] = transforms, cssProperties.push(transform)
      if (duration > 0 && typeof properties === 'object') {
        cssValues[transitionProperty] = cssProperties.join(', ')
        cssValues[transitionDuration] = duration + 's'
        cssValues[transitionDelay] = delay + 's'
        cssValues[transitionTiming] = (ease || 'linear')
      }
    }

    wrappedCallback = function(event){
      if (typeof event !== 'undefined') {
        if (event.target !== event.currentTarget) return // makes sure the event didn't bubble from "below"
        $(event.target).unbind(endEvent, wrappedCallback)
      } else
        $(this).unbind(endEvent, wrappedCallback) // triggered by setTimeout

      fired = true
      $(this).css(cssReset)
      callback && callback.call(this)
    }
    if (duration > 0){
      this.bind(endEvent, wrappedCallback)
      // transitionEnd is not always firing on older Android phones
      // so make sure it gets fired
      setTimeout(function(){
        if (fired) return
        wrappedCallback.call(that)
      }, ((duration + delay) * 1000) + 25)
    }

    // trigger page reflow so new elements can animate
    this.size() && this.get(0).clientLeft

    this.css(cssValues)

    if (duration <= 0) setTimeout(function() {
      that.each(function(){ wrappedCallback.call(this) })
    }, 0)

    return this
  }

  testEl = null
})(Zepto)
;var org = (function () {
    document.body.addEventListener('touchstart', function () {
    }); //ios 触发active渲染
    var lib = {
        scriptName: 'mobile.js',
        _ajax: function (options) {
            $.ajax({
                url: options.url,
                type: options.type,
                data: options.data,
                dataType: options.dataType,
                async: options.async,
                beforeSend: function (xhr, settings) {
                    options.beforeSend && options.beforeSend(xhr);
                    //django配置post请求
                    if (!lib._csrfSafeMethod(settings.type) && lib._sameOrigin(settings.url)) {
                        xhr.setRequestHeader('X-CSRFToken', lib._getCookie('csrftoken'));
                    }
                },
                success: function (data) {
                    options.success && options.success(data);
                },
                error: function (xhr) {
                    options.error && options.error(xhr);
                },
                complete: function () {
                    options.complete && options.complete();
                }
            });
        },
        _calculate: function (dom, callback) {
            var calculate = function (amount, rate, period, pay_method) {
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

            dom.on('input', function () {
                _inputCallback();
            });

            function _inputCallback() {
                var earning, earning_element, earning_elements, fee_earning, jiaxi_type;
                var target = $('input[data-role=p2p-calculator]'),
                    existing = parseFloat(target.attr('data-existing')),
                    period = target.attr('data-period'),
                    rate = target.attr('data-rate') / 100,
                    pay_method = target.attr('data-paymethod');
                activity_rate = target.attr('activity-rate') / 100;
                activity_jiaxi = target.attr('activity-jiaxi') / 100;
                amount = parseFloat(target.val()) || 0;

                if (amount > target.attr('data-max')) {
                    amount = target.attr('data-max');
                    target.val(amount);
                }
                activity_rate += activity_jiaxi;
                amount = parseFloat(existing) + parseFloat(amount);
                earning = calculate(amount, rate, period, pay_method);
                fee_earning = calculate(amount, activity_rate, period, pay_method);

                if (earning < 0) {
                    earning = 0;
                }
                earning_elements = (target.attr('data-target')).split(',');
                jiaxi_type = target.attr('jiaxi-type');
                for (var i = 0; i < earning_elements.length; i++) {
                    earning_element = earning_elements[i];
                    if (earning) {
                        fee_earning = fee_earning ? fee_earning : 0.00;
                        if(jiaxi_type === "+"){
                            $(earning_element).html(earning+'+<span class="blue">'+fee_earning+'</span>').data("val",(earning + fee_earning));
                        }else{
                            earning += fee_earning;
                            $(earning_element).text(earning.toFixed(2)).data("val",(earning + fee_earning));
                        }
                    } else {
                        //$(earning_element).text("0.00");
                        $(earning_element).html('0+<span class="blue">0.00</span>').data("val",0);
                    }
                }
                callback && callback();
            }
        },
        _getQueryStringByName: function (name) {
            var result = location.search.match(new RegExp('[\?\&]' + name + '=([^\&]+)', 'i'));
            if (result == null || result.length < 1) {
                return '';
            }
            return result[1];
        },
        _getCookie: function (name) {
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
        _csrfSafeMethod: function (method) {
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        },
        _sameOrigin: function (url) {
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = '//' + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
        },
        _setShareData: function (ops, suFn, canFn) {
            var setData = {};
            if (typeof ops == 'object') {
                for (var p in ops) {
                    setData[p] = ops[p];
                }
            }
            typeof suFn == 'function' && suFn != 'undefined' ? setData.success = suFn : '';
            typeof canFn == 'function' && canFn != 'undefined' ? setData.cancel = canFn : '';
            return setData
        },
        /*
         * 分享到微信朋友
         */
        _onMenuShareAppMessage: function (ops, suFn, canFn) {
            wx.onMenuShareAppMessage(lib._setShareData(ops, suFn, canFn));
        },
        /*
         * 分享到微信朋友圈
         */
        _onMenuShareTimeline: function (ops, suFn, canFn) {
            wx.onMenuShareTimeline(lib._setShareData(ops, suFn, canFn));
        },
        _onMenuShareQQ: function () {
            wx.onMenuShareQQ(lib._setShareData(ops, suFn, canFn));
        }
    }
    return {
        scriptName: lib.scriptName,
        ajax: lib._ajax,
        calculate: lib._calculate,
        getQueryStringByName: lib._getQueryStringByName,
        getCookie: lib._getCookie,
        csrfSafeMethod: lib._csrfSafeMethod,
        sameOrigin: lib._sameOrigin,
        onMenuShareAppMessage: lib._onMenuShareAppMessage,
        onMenuShareTimeline: lib._onMenuShareTimeline,
        onMenuShareQQ: lib._onMenuShareQQ,
    }
})();

org.ui = (function () {
    var lib = {
        _alert: function (txt, callback) {
            if (document.getElementById("alert-cont")) {
                document.getElementById("alertTxt").innerHTML = txt;
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
            } else {
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText = "position:fixed;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
                var alertFram = document.createElement("DIV");
                alertFram.id = "alert-cont";
                alertFram.style.cssText = "position:fixed; top:35%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
                strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 1.25rem .75rem;'>" + txt + "</div>";
                strHtml += " <div class='popub-footer' style='width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;'>确认</div>";
                alertFram.innerHTML = strHtml;
                document.body.appendChild(alertFram);
                document.body.appendChild(shield);
            }
            $('.popub-footer').on('click', function () {
                $('#alert-cont, #popubMask').hide()
                callback && callback();
            })
            document.body.onselectstart = function () {
                return false;
            };
        },
        _confirm: function (title, certainName, callback, callbackData) {
            if ($('.confirm-warp').length > 0) {
                $('.confirm-text').text(title);
                $('.confirm-certain').text(certainName);
                $('.confirm-warp').show();

                $('.confirm-cancel').on('click', function (e) {
                    $('.confirm-warp').hide();
                })
                $('.confirm-certain').on('click', function (e) {
                    $('.confirm-warp').hide();

                    if (callback) {
                        callbackData ? callback(callbackData) : callback();
                    }
                })
            }
        },
        _showSign: function (signTxt, callback) {
            var $sign = $('.error-sign');
            if ($sign.length == 0) {
                $('body').append("<section class='error-sign'>" + signTxt + "</section>");
                $sign = $('.error-sign');
            } else {
                $sign.text(signTxt)
            }
            ~function animate() {
                $sign.css('display', 'block');
                setTimeout(function () {
                    $sign.css('opacity', 1);
                    setTimeout(function () {
                        $sign.css('opacity', 0);
                        setTimeout(function () {
                            $sign.hide();
                            return callback && callback();
                        }, 300)
                    }, 1000)
                }, 0)
            }()
        },
        /*
         .form-list
         .form-icon.user-phone(ui targer).identifier-icon（事件target）
         .form-input
         input(type="tel", name="identifier", placeholder="请输入手机号",data-target2='identifier-icon'（事件target）, data-icon='user-phone'(ui事件), data-target="identifier-edit"(右侧操作), data-empty=''（input val空的时候的classname）, data-val='input-clear'（input val不为空的时候的classname）).foreach-input
         .form-edit-icon.identifier-edit（右边操作如：清空密码）
         */
        _inputStyle: function (options) {
            var $submit = options.submit,
                inputArrList = options.inputList;

            $.each(inputArrList, function (i) {
                inputArrList[i]['target'].on('input', function () {
                    var $self = $(this);
                    if ($self.val() == '') {
                        inputForClass([
                            {
                                target: $self.attr('data-target'),
                                addName: $self.attr('data-empty'),
                                reMove: $self.attr('data-val')
                            },
                            {
                                target: $self.attr('data-target2'),
                                addName: $self.attr('data-icon'),
                                reMove: ($self.attr('data-icon') + "-active")
                            }
                        ],$self);
                        $submit.attr('disabled', true);
                    } else {
                        inputForClass([
                            {
                                target: $self.attr('data-target'),
                                addName: $self.attr('data-val'),
                                reMove: $self.attr('data-empty')
                            },
                            {
                                target: $self.attr('data-target2'),
                                addName: ($self.attr('data-icon') + "-active"),
                                reMove: $self.attr('data-icon')
                            }
                        ],$self);
                    }
                    var disabledBg = 'rgba(219,73,63,.5)', activeBg = 'rgba(219,73,63,1)';
                    if (options.submitStyle) {
                        disabledBg = options.submitStyle.disabledBg || 'rgba(219,73,63,.5)';
                        activeBg = options.submitStyle.activeBg || 'rgba(219,73,63,1)';
                    }
                    canSubmit() ? $submit.css('background', activeBg).removeAttr('disabled') : $submit.css('background', disabledBg).attr('disabled',true)
                })
            });

            //用户名一键清空
            $('.identifier-edit').on('click', function (e) {
                $(this).siblings().val('').trigger('input');
            });
            //密码隐藏显示
            $('.password-handle').on('click', function () {
                if ($(this).hasClass('hide-password')) {
                    $(this).addClass('show-password').removeClass('hide-password');
                    $(this).siblings().attr('type', 'text');
                } else if ($(this).hasClass('show-password')) {
                    $(this).addClass('hide-password').removeClass('show-password');
                    $(this).siblings().attr('type', 'password');
                }
            });

            var inputForClass = function (ops, t) {
                if(!typeof(ops) === 'object') return ;
                var targetDom;
                $.each(ops, function(i){
                    if(t && t.siblings('.'+ops[i].target).length > 0){
                        targetDom = t.siblings('.'+ops[i].target);
                    }else{
                        targetDom = $('.'+ops[i].target);
                    }
                    targetDom.addClass(ops[i].addName).removeClass(ops[i].reMove);
                });
            }
            var returnCheckArr = function () {
                var returnArr = [];
                for (var i = 0; i < arguments.length; i++) {
                    for (var arr in arguments[i]) {
                        if (arguments[i][arr]['required'])
                            returnArr.push(arguments[i][arr]['target']);
                    }
                }
                return returnArr
            }
            var canSubmit = function () {
                var isPost = true, newArr = [];

                newArr = returnCheckArr(options.inputList, options.otherTarget);

                $.each(newArr, function (i, dom) {
                    if (dom.attr('type') == 'checkbox') {
                        if (!dom.attr('checked'))
                            return isPost = false
                    } else if (dom.val() == '')
                        return isPost = false
                })

                return isPost
            }
        },
    }

    return {
        focusInput: lib._inputStyle,
        showSign: lib._showSign,
        alert: lib._alert,
        confirm: lib._confirm
    }
})();

org.login = (function (org) {
    var lib = {
        $captcha_img: $('#captcha'),
        $captcha_key: $('input[name=captcha_0]'),
        init: function () {
            //lib._captcha_refresh();
            lib._checkFrom();
        },
        _captcha_refresh: function () {
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function (res) {
                lib.$captcha_img.attr('src', res['image_url']);
                lib.$captcha_key.val(res['key']);
            });
        },
        _checkFrom: function () {
            var $form = $('#login-form'),
                $submit = $form.find('button[type=submit]');
            org.ui.focusInput({
                submit: $('button[type=submit]'),
                inputList: [
                    {target: $('input[name=identifier]'), required: true},
                    {target: $('input[name=password]'), required: true},
                ],
            });

            //刷新验证码
            //lib.$captcha_img.on('click', function() {
            //  lib._captcha_refresh();
            //});
            $submit.on('click', function () {
                var data = {
                    'identifier': $.trim($form.find('input[name=identifier]').val()),
                    'password': $.trim($form.find('input[name=password]').val())
                    //'openid': $.trim($form.find('input[name=openid]').val())
                };
                org.ajax({
                    'type': 'post',
                    'url': $form.attr('action'),
                    'data': data,
                    beforeSend: function (xhr) {
                        $submit.attr('disabled', true).text('登录中..');
                    },
                    success: function (res) {
                        if(res.re_code != 0){
                            window.location.href = "/weixin/jump_page/?message="+res.errmessage;
                        }else{
                            window.location.href = "/weixin/jump_page/?message=您已登录并绑定成功";
                        }
                    },
                    error: function (res) {
                        if (res['status'] == 403) {
                            org.ui.showSign('请勿重复提交');
                            return false;
                        }
                        var data = JSON.parse(res.responseText);
                        for (var key in data) {
                            data['__all__'] ? org.ui.showSign(data['__all__']) : org.ui.showSign(data[key]);
                        }
                        lib._captcha_refresh()
                    },
                    complete: function () {
                        $submit.removeAttr('disabled').text('登录并关联网利宝账号');
                    }
                });
                return false;
            });
        }
    }
    return {
        init: lib.init
    }


})(org);

org.regist = (function (org) {
    var lib = {
        $captcha_img: $('#captcha'),
        $captcha_key: $('input[name=captcha_0]'),
        init: function () {
            lib._onlytrue();
            lib._captcha_refresh();
            lib._checkFrom();
            lib._animateXieyi();
        },
        _onlytrue: function () {
            var onlyture = org.getQueryStringByName('onlyphone');
            if (onlyture && onlyture == 'true') {
                $('input[name=identifier]').attr('readOnly', true);
            }
        },
        _animateXieyi: function () {
            var $submitBody = $('.submit-body'),
                $protocolDiv = $('.regist-protocol-div'),
                $cancelXiyi = $('.cancel-xiyie'),
                $showXiyi = $('.xieyi-btn'),
                $agreement = $('#agreement');
            //是否同意协议
            $agreement.change(function () {
                if ($(this).attr('checked') == 'checked') {
                    $submitBody.addClass('disabled').attr('disabled', 'disabled');
                    return $(this).removeAttr('checked');
                } else {
                    $submitBody.removeClass('disabled').removeAttr('disabled');
                    return $(this).attr('checked', 'checked');
                }
            });
            //显示协议
            $showXiyi.on('click', function (event) {
                event.preventDefault();
                $protocolDiv.css('display', 'block');
                setTimeout(function () {
                    $protocolDiv.css('top', '0%');
                }, 0)
            });
            //关闭协议
            $cancelXiyi.on('click', function () {
                $protocolDiv.css('top', '100%');
                setTimeout(function () {
                    $protocolDiv.css('display', 'none');
                }, 200)
            });
        },
        _captcha_refresh: function () {
            var captcha_refresh_url = '/captcha/refresh/?v=' + new Date().getTime();
            $.get(captcha_refresh_url, function (res) {
                lib.$captcha_img.attr('src', res['image_url']);
                lib.$captcha_key.val(res['key']);
            });
        },
        _checkFrom: function () {
            var $submit = $('button[type=submit]'),
                $identifier = $('input[name=identifier]'),
                $password = $('input[name=password]'),
                $validation = $('input[name=validation]'),
                $invitation = $('input[name=invitation]'),
                $agreement = $('input[name=agreement]'),
                $captcha_0 = $('input[name=captcha_0]'),
                $captcha_1 = $('input[name=captcha_1]');


            org.ui.focusInput({
                submit: $submit,
                inputList: [
                    {target: $identifier, required: true},
                    {target: $password, required: true},
                    {target: $validation, required: true},
                    {target: $invitation, required: false},
                    {target: $captcha_1, required: true}
                ],
                otherTarget: [{target: $agreement, required: true}]
            });
            $("#agreement").on('click', function () {
                $(this).toggleClass('agreement');
                $(this).hasClass('agreement') ? $(this).find('input').attr('checked', 'checked') : $(this).find('input').removeAttr('checked');
                $identifier.trigger('input')
            })
            //刷新验证码
            lib.$captcha_img.on('click', function () {
                lib._captcha_refresh();
            });


            //手机验证码
            $('.request-check').on('click', function () {
                var phoneNumber = $identifier.val(),
                    $that = $(this), //保存指针
                    count = 60,  //60秒倒计时
                    intervalId; //定时器

                if (!check['identifier'](phoneNumber, 'phone')) return  //号码不符合退出
                $that.attr('disabled', 'disabled').addClass('regist-alreay-request');
                org.ajax({
                    url: '/api/phone_validation_code/register/' + phoneNumber + '/',
                    data: {
                        captcha_0: $captcha_0.val(),
                        captcha_1: $captcha_1.val(),
                    },
                    type: 'POST',
                    error: function (xhr) {
                        clearInterval(intervalId);
                        var result = JSON.parse(xhr.responseText);
                        org.ui.showSign(result.message);
                        $that.text('获取验证码').removeAttr('disabled').removeClass('regist-alreay-request');
                        lib._captcha_refresh();
                    }
                });
                //倒计时
                var timerFunction = function () {
                    if (count >= 1) {
                        count--;
                        return $that.text(count + '秒后可重发');
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
            var check = {
                identifier: function (val) {
                    var isRight = false,
                        re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/);
                    re.test($.trim(val)) ? isRight = true : (org.ui.showSign('请输入正确的手机号'), isRight = false);
                    return isRight;
                },
                password: function (val) {
                    if (6 > $.trim(val).length || $.trim(val).length > 20) {
                        org.ui.showSign('密码为6-20位数字/字母/符号/区分大小写')
                        return false
                    }
                    return true
                }
            }
            var checkList = [$identifier, $password],
                isSubmit = true;

            var invite_phone = org.getQueryStringByName('parentPhone') == '' ? '' : org.getQueryStringByName('parentPhone');
            $submit.on('click', function () {
                isSubmit = true;
                //校验主函数
                $.each(checkList, function () {
                    var value = $(this).val(), checkTarget = $(this).attr('name');
                    if (!check[checkTarget](value)) {
                        return isSubmit = false
                    }
                });

                if (!isSubmit) return false;
                var tid = org.getQueryStringByName('tid');
                var token = $invitation.val() === '' ? $('input[name=token]').val() : $invitation.val();
                org.ajax({
                    url: '/api/register/',
                    type: 'POST',
                    data: {
                        'identifier': $identifier.val(),
                        'password': $password.val(),
                        'captcha_0': $captcha_0.val(),
                        'captcha_1': $captcha_1.val(),
                        'validate_code': $validation.val(),
                        'invite_code': token,
                        'tid': tid,
                        'invite_phone': invite_phone
                    },
                    beforeSend: function () {
                        $submit.text('注册中,请稍等...');
                    },
                    success:function(data){
                        if(data.ret_code === 0){
                           var next = '/weixin/sub_regist_first/?phone='+$identifier.val();
                            next = org.getQueryStringByName('mobile') == '' ? next : next + '&mobile='+ org.getQueryStringByName('mobile');
                            next = org.getQueryStringByName('serverId') == '' ? next : next + '&serverId='+ org.getQueryStringByName('serverId');
                            //console.log(next);
                            window.location.href = next;
                        } else if (data.ret_code > 0) {
                            org.ui.showSign(data.message);
                            $submit.text('立即注册 ｜ 领取奖励');
                        }
                    },
                    error: function (xhr) {
                        var result = JSON.parse(xhr.responseText);
                        if (xhr.status === 429) {
                            org.ui.alert('系统繁忙，请稍候重试')
                        } else {
                            org.ui.alert(result.message);
                        }
                    },
                    complete: function () {
                        $submit.text('立即注册 ｜ 领取奖励');
                    }
                });
            })
        }
    };
    return {
        init: lib.init
    }
})(org);

org.list = (function (org) {
    var lib = {
        windowHeight: $(window).height(),
        canGetPage: true, //防止多次请求
        scale: 0.8, //页面滚到百分70的时候请求
        pageSize: 10, //每次请求的个数
        page: 2, //从第二页开始
        init: function () {
            lib._swiper();
            lib._scrollListen();
        },
        _swiper: function () {
            var autoplay = 5000, //焦点图切换时间
                loop = true,  //是否无缝滚动
                $swiperSlide = $('.swiper-slide');

            if ($swiperSlide.length / 2 < 1) {
                autoplay = 0;
                loop = false;
            }

        },
        _scrollListen: function () {
            $('.load-body').on('click', function () {
                lib.canGetPage && lib._getNextPage();
            })
        },
        _getNextPage: function () {
            org.ajax({
                type: 'GET',
                url: '/api/p2ps/wx/',
                data: {page: lib.page, 'pagesize': lib.pageSize},
                beforeSend: function () {
                    lib.canGetPage = false;
                    $('.load-text').html('加载中...');
                },
                success: function (data) {
                    $('#list-body').append(data.html_data);
                    lib.page++;
                    lib.canGetPage = true;

                },
                error: function () {
                    org.ui.alert('Ajax error!')
                },
                complete: function () {
                    $('.load-text').html('点击查看更多项目');
                }
            })
        }

    };
    return {
        init: lib.init
    }
})(org);

org.detail = (function (org) {
    var lib = {
        weiURL: '/weixin/api/jsapi_config/',
        countDown: $('#countDown'),
        init: function () {
            lib._tab();
            lib._animate();
            //lib._share();
            lib.countDown.length > 0 && lib._countDown(lib.countDown);
            lib._downPage();
        },
        /*
         * 页面动画
         */
        _animate: function () {
            $(function () {
                var $progress = $('.progress-percent'),
                    $payalert = $('.new-pay');
                setTimeout(function () {
                    var percent = parseFloat($progress.attr('data-percent'));
                    if (percent == 100) {
                        $progress.css('margin-top', '-10%');
                    } else {
                        $progress.css('margin-top', (100 - percent) + '%');
                    }
                    setTimeout(function () {
                        $progress.addClass('progress-bolang')
                    }, 1000)
                }, 300)
            })
        },
        /*
         * 公司信息tab
         */
        _tab: function () {
            $('.toggleTab').on('click', function () {
                $(this).siblings().toggle();
                $(this).find('span').toggleClass('icon-rotate');
            })
        },
        /*
        * 微信分享
         */
        _share: function(obj){
            var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ'];
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
                var host = 'https://www.wanglibao.com',
                    shareImg,//图片
                    shareLink,//连接地址
                    shareMainTit,//分享标题
                    shareBody,//分享描述
                    success;
                var conf = $.extend({
                    shareImg: host + '/static/imgs/sub_weixin/logo.png',//图片
                    shareLink: host + '/weixin/award_index/',//连接地址
                    shareMainTit: '幸运大转盘，日日有惊喜',//分享标题
                    shareBody: '转盘一动，大奖即送。还不快快领取！',//分享描述
                    success: function(){//成功事件
                    }
                }, obj || {});
                shareImg = conf.shareImg;
                shareLink = conf.shareLink;//连接地址
                shareMainTit = conf.shareMainTit;//分享标题
                shareBody = conf.shareBody;//分享描述
                success = conf.success;
                //alert(shareMainTit);
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg,
                    success: function(){
                        //alert(shareMainTit);
                        success && success();
                    }
                });
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: shareMainTit,
                    link : shareLink,
                    imgUrl: shareImg,
                    success: function(){
                        //alert(shareMainTit);
                        success && success();
                    }
                });
                //分享给QQ
                org.onMenuShareQQ({
                    title: shareMainTit,
                    desc: shareBody,
                    link : shareLink,
                    imgUrl: shareImg,
                    success: function(){
                        success && success();
                    }
                });
            })
        },
        /*
         * 倒计时
         */
        _countDown: function (target) {
            var endTimeList = target.attr('data-left').replace(/-/g, '/');
            var TimeTo = function (dd) {
                var t = new Date(dd),
                    n = parseInt(new Date().getTime()),
                    c = t - n;
                if (c <= 0) {
                    target.text('活动已结束');
                    clearInterval(window['interval']);
                    return
                }
                var ds = 60 * 60 * 24 * 1000,
                    d = parseInt(c / ds),
                    h = parseInt((c - d * ds) / (3600 * 1000)),
                    m = parseInt((c - d * ds - h * 3600 * 1000) / (60 * 1000)),
                    s = parseInt((c - d * ds - h * 3600 * 1000 - m * 60 * 1000) / 1000);
                m < 10 ? m = '0' + m : '';
                s < 10 ? s = '0' + s : '';
                target.text(d + '天' + h + '小时' + m + '分' + s + '秒');
            }
            window['interval'] = setInterval(function () {
                TimeTo(endTimeList);
            }, 1000);
        },
        _downPage: function () {
            var
                u = navigator.userAgent,
                ua = navigator.userAgent.toLowerCase(),
                footer = document.getElementById('footer-down'),
                isAndroid = u.indexOf('Android') > -1 || u.indexOf('Linux') > -1,
                isiOS = !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
            $('#down-btn').on('click', function () {
                if (ua.match(/MicroMessenger/i) == "micromessenger") {
                    window.location.href = 'http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao&g_f=991653';
                } else {
                    if (isiOS) {
                        window.location.href = 'https://itunes.apple.com/cn/app/wang-li-bao/id881326898?mt=8';
                    } else if (isAndroid) {
                        window.location.href = 'https://www.wanglibao.com/static/wanglibao1.apk';
                    } else {
                        window.location.href = 'http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao&g_f=991653';
                    }
                }
            })
        }
    }
    return {
        init: lib.init,
        share: lib._share
    }
})(org);

org.buy = (function (org) {
    var lib = {
        redPackSelect: $('#gifts-package'),
        amountInout: $('input[data-role=p2p-calculator]'),
        $redpackSign: $('.redpack-sign'),
        $redpackForAmount: $('.redpack-for-amount'),
        showredPackAmount: $(".redpack-amount"),
        showAmount: $('.need-amount'),
        redPackAmount: 0,
        isBuy: true, //防止多次请求，后期可修改布局用button的disable，代码罗辑会少一点
        buy_amount: null,
        init: function () {
            lib._checkRedpack();
            lib._calculate();
            lib._buy();
            lib._amountInp();
            lib._closePage();
        },
        _amountInp: function(){ //金额输入
            lib.amountInout.on("input",function(){
                var self = $(this),
                    val = self.val();
                if(val != ""){
                    $(".snap-up").removeAttr("disabled").css("opacity",1);
                }else{
                    $(".snap-up").attr("disabled",true).css("opacity",0.5);
                }
                lib._setRedpack();
                //lib.showAmount.text(val);
            });
        },
        _checkRedpack: function () {
            var productID = $(".invest-one").attr('data-protuctid');
            org.ajax({
                type: 'POST',
                url: '/api/redpacket/selected/',
                data: {product_id: productID},
                success: function (data) {
                    if (data.ret_code === 0) {
                        if (data.used_type == 'redpack')
                            $('.redpack-already').html(data.message).show();
                        else if (data.used_type == 'coupon') {
                            lib.amountInout.attr('activity-jiaxi', data.amount);
                            $('.redpack-already').show().find('.already-amount').text(data.amount + '%');
                        }

                    }
                }
            });
        },
        /*
         * 购买页收益计算器
         */
        _calculate: function () {
            org.calculate(lib.amountInout, lib._setRedpack)
        },
        /*
         *   购买提示信息
         *   触发_setRedpack条件 选择红包，投资金额大于0
         *
         *
         */
        _setRedpack: function () {
            var redPack = lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex),//选择的select项
                redPackVal = parseFloat(lib.redPackSelect.find('option').eq(lib.redPackSelect.get(0).selectedIndex).attr('data-amount')),
                inputAmount = parseInt(lib.amountInout.val()), //输入框金额
                redPackAmount = redPack.attr("data-amount"), //红包金额
                redPackMethod = redPack.attr("data-method"), //红包类型
                redPackInvestamount = parseInt(redPack.attr("data-investamount")),//红包门槛
                redPackHighest_amount = parseInt(redPack.attr("data-highest_amount")),//红包最高抵扣（百分比红包才有）
                repPackDikou = 0,
                senderAmount = inputAmount; //实际支付金额;

            lib.redPackAmountNew = 0;
            inputAmount = isNaN(inputAmount) ? "0.00" : inputAmount;
            if (redPackVal) { //如果选择了红包
                if (!inputAmount) {
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    //lib.$redpackSign.hide();//红包直抵提示
                    lib.showAmount.text(inputAmount);//实际支付
                    return
                }

                if (inputAmount < redPackInvestamount) {
                    lib.$redpackSign.hide();//红包直抵提示
                    lib.$redpackForAmount.hide();//请输入投资金额
                    //lib.showAmount.text(senderAmount);//实际支付金额
                    return $(".redpack-investamount").show();//未达到红包使用门槛
                } else {
                    lib.amountInout.attr('activity-jiaxi', 0);
                    if (redPackMethod == '*') { //百分比红包
                        //如果反回来的百分比需要除于100 就把下面if改成if (inputAmount * redPackAmount/100 > redPackHighest_amount)
                        if (inputAmount * redPackAmount >= redPackHighest_amount && redPackHighest_amount > 0) {//是否超过最高抵扣
                            repPackDikou = redPackHighest_amount;
                        } else {//没有超过最高抵扣
                            repPackDikou = inputAmount * redPackAmount;
                        }
                    } else if (redPackMethod == '~') {
                        lib.amountInout.attr('activity-jiaxi', redPackAmount * 100);
                        repPackDikou = 0;
                        lib.$redpackSign.hide();
                    } else {  //直抵红包
                        repPackDikou = parseInt(redPackAmount);
                    }
                    senderAmount = inputAmount - repPackDikou;
                    lib.redPackAmountNew = repPackDikou;
                    if (redPackMethod != '~') {
                        lib.showredPackAmount.text(repPackDikou);//红包抵扣金额
                        lib.$redpackSign.show();//红包直抵提示
                    }
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                }
            } else {
                lib.$redpackSign.hide();//红包直抵提示
            }
            senderAmount = isNaN(senderAmount) ? "0.00" : senderAmount;
            lib.showAmount.text(senderAmount);//实际支付金额
            lib.$redpackForAmount.hide();//请输入投资金额

        },
        _buy: function () {
            var $buyButton = $('button[name=submit]'),
                $redpack = $("#gifts-package");
            var noBank = $("#page-onRegister");
            if(noBank.length > 0 && noBank.is("hidden")){

            }
            //红包select事件
            $redpack.on("change", function () {
                if ($(this).val() != '') {
                    lib.amountInout.val() == '' ? $('.redpack-for-amount').show() : lib._setRedpack();
                } else {
                    lib.amountInout.attr('activity-jiaxi', 0);
                    $(".redpack-investamount").hide();//未达到红包使用门槛
                    lib.$redpackSign.hide();
                }
                return lib.amountInout.trigger('input');
            });

            $buyButton.on('click', function () {
                var $buySufficient = $('#page-onMoney'),
                    balance = parseFloat($("#balance").attr("data-value")),
                    amount = $('.amount').val() * 1,
                    productID = $(".invest-one").attr('data-protuctid');
                if (amount) {
                    if (amount % 100 !== 0) return org.ui.alert('请输入100的倍数金额');
                    if (amount > balance)  return $buySufficient.show();
                } else {
                    return org.ui.alert('请输入正确的金额');
                }
                var redpackValue = $redpack[0].options[$redpack[0].options.selectedIndex].value;
                if (!redpackValue || redpackValue == '') {
                    redpackValue = null;
                }

                var post_data = {
                    amount: amount,
                    product: productID,
                    redpack: redpackValue
                };
                org.ui.confirm("购买金额为" + amount, '确认投资', lib._trade_pwd_seach, post_data);

            })
        },
        _trade_pwd_seach: function(post_data){
            org.ajax({
                url: '/api/profile/',
                type: 'GET',
                success: function(result){
                    result.trade_pwd_is_set ? lib._trade_pws_operation(true, post_data): lib._trade_pws_operation(false, post_data);
                }
            })

        },
        _trade_pws_operation: function(state, post_data){
            if(state){
                entry_ui()
            }else{
                set_ui()
            }

            function entry_ui(){
                var entry_operation = new Deal({
                    title: '请输入交易密码',
                    sign: '投资金额<br>￥'+ post_data.amount,
                    target: $('input[name=password1]'),
                    done : function(pwd){
                        entry_operation.show_loading();
                        post_data.trade_pwd = pwd;
                        lib._buy_operation(entry_operation,post_data);

                    }
                });
                entry_operation.init();
                entry_operation.show();
            }

            var password_1 = null, password_2 = null ;

            function set_ui(){
                var operation_1 = new Deal({
                    title: '设置交易密码',
                    sign: '请设置6位数字作为交易密码',
                    target: $('input[name=password1]'),
                    done : function(pwd){
                        password_1 = pwd;
                        operation_1.clear();
                        operation_1.hide();
                        operation_2();
                    }
                });
                operation_1.init();
                operation_1.show();

                function operation_2(){
                    var operation_2 = new Deal({
                        title: '设置交易密码',
                        sign: '请再次确认交易密码',
                        target: $('input[name=password2]'),
                        done : function(pwd){
                            password_2 = pwd;

                            if(password_2 != password_1){
                                operation_2.clear();
                                operation_2.hide();
                                return Deal_ui.show_alert('error', function(){
                                    set_ui()
                                })
                            }
                            operation_2.show_loading();
                            lib._trade_pws_set(operation_2, password_2,post_data);
                        }
                    });
                    operation_2.init();
                    operation_2.show();
                }
            }

        },
        _trade_pws_set: function(entry_operation, new_trade_pwd,post_data){
            org.ajax({
                url: '/api/trade_pwd/',
                type: 'post',
                data: {
                    action_type: 1,
                    new_trade_pwd: new_trade_pwd
                },
                success: function(result){
                    entry_operation.hide_loading();
                    entry_operation.clear();
                    entry_operation.hide();
                    if(result.ret_code == 0){
                        //Deal_ui.show_alert('success', function(){
                        //    window.location = window.location.href;
                        //}, '交易密码设置成功，请牢记！');
                        post_data.trade_pwd = new_trade_pwd;
                        lib._buy_operation(entry_operation,post_data);
                    }

                    if(result.ret_code > 0 ){
                        org.ui.alert(result.message);
                    }
                }
            })
        },
        _buy_operation: function(entry_operation, post_data){
            var $buyButton = $('button[name=submit]');
            var balance = parseFloat($("#balance").attr("data-value"));
            org.ajax({
                type: 'POST',
                url: '/api/p2p/purchase/mobile/',
                data:  post_data,
                beforeSend: function () {
                    $buyButton.attr('disabled',true).text("抢购中...");
                },
                success: function(result){
                    entry_operation.hide_loading();
                    entry_operation.clear();
                    entry_operation.hide();
                    if(result.ret_code == 0){
                        $('.balance-sign').text(balance - result.data + lib.redPackAmountNew + '元');
                        $("#page-ok").css("display","-webkit-box");
                        return;
                    }

                    if(result.ret_code == 30047){
                        Deal_ui.show_entry(result.retry_count, function(){
                            entry_operation.show();
                        });
                        return;
                    }
                    if(result.ret_code == 30048){
                        Deal_ui.show_lock('取消', '找回密码', '交易密码已被锁定，请3小时后再试',function(){
                            window.location = '/weixin/sub_pwd_back/?next=/weixin/sub_detail/detail/'+post_data.product+ '/';
                        });
                        return;
                    }
                    if(result.error_number > 0){
                        return org.ui.alert(result.message);
                    }
                },
                error: function (xhr) {
                    org.ui.alert('服务器异常');
                },
                complete: function () {
                    $buyButton.removeAttr('disabled').text("立即投资");
                }
            })
        },
        _closePage: function(){
            $(".back-fwh").on("click",function(){
                closePage();
            });
        }
    }
    return {
        init: lib.init
    }
})(org);

org.calculator = (function (org) {
    var lib = {
        init: function () {
            org.calculate($('input[data-role=p2p-calculator]'))
            lib._addEvenList();
        },
        _addEvenList: function () {
            var $calculatorBuy = $('.calculator-buy'),
                $countInput = $('.count-input'),
                productId, amount_profit, amount;

            $calculatorBuy.on('click', function () {
                productId = $(this).attr('data-productid');
                amount = $countInput.val();
                amount_profit = $("#expected_income").text();
                if (amount % 100 !== 0 || amount == '') {
                    return org.ui.alert("请输入100的整数倍")
                } else {
                    window.location.href = '/weixin/view/buy/' + productId + '/?amount=' + amount + '&amount_profit=' + amount_profit;
                }
            })
        }

    }
    return {
        init: lib.init
    }
})(org);

org.recharge = (function (org) {
    var lib = {
        $recharge: $('button[name=submit]'),
        $amount: $("input[name='amount']"),
        $vcode: $('input[name=vcode]'),
        $card_no: $("input[name='card_no']"),
        $recharge_body: $('.recharge-main'),
        $load: $(".recharge-loding"),
        $validationBody: $('.validation-warp'),
        re: new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/),
        $card_warp: $('.card-warp'),
        $bank_name: $(".bank-txt-name"),
        data: null,
        init: function () {
            lib.the_one_card();
            lib._close_alt($(".continue-rechare"));
        },
        /**
         * 判断有没有同卡进出的卡
         */
        the_one_card: function () {
            var _self = this;
            org.ajax({
                type: 'get',
                url: '/api/pay/the_one_card/',
                success: function (data) {
                    //同卡进出
                   _self.on_card_operation(data);
                },
                error: function (data) {
                    //没有同卡进出
                    if (data.status === 403) {
                        _self.fetchBankList();
                    }
                }
            })
        },
        on_card_operation: function(data){
            var _self = this,
            card = data.no.slice(0, 6) + '********' + data.no.slice(-4);
            _self.$load.hide();
            _self.$recharge_body.show();
            _self.data = data;
            _self.$amount.attr('placeholder', '该银行单笔限额' + data.bank.bank_limit.second_one/10000+'万元');
            _self.$card_no.val(card);
            _self.$bank_name.text(data.bank.name);
            lib._rechargeThe_one_card();
        },
        fetchBankList: function () {
            var _self = this;
            org.ajax({
                url: '/api/pay/cnp/list_new/',
                type: 'POST',
                success: function (data) {
                    if (data.ret_code === 0) {
                        _self.$load.hide();
                        data.cards.length === 0 ? $('.unbankcard').show() : $('.bankcard').show();
                    }
                    if (data.ret_code > 0 && data.ret_code != 20071) {
                        return org.ui.alert(data.message);
                    }
                },
                error: function (data) {
                    return org.ui.alert('系统异常，请稍后再试');
                }
            })
        },
        /**
         * 绑定同卡进出的卡充值
         * @private
         */
        _rechargeThe_one_card: function () {
            var _self = this;
            _self.$recharge.on('click', function () {
                var
                    card_no = _self.data.no,
                    gate_id = _self.data.bank.gate_id,
                    amount = _self.$amount.val() * 1;

                var sort_card = card_no.slice(0, 6) + card_no.slice(-4);

                if (amount == 0 || !amount) {
                    return org.ui.showSign('请输入充值金额')
                }

                var data = {
                    data: {
                        phone: '',
                        card_no: sort_card,
                        amount: amount,
                        gate_id: gate_id
                    },
                    beforeSend: function () {
                        _self.$recharge.attr('disabled', true).text("充值中..");
                    },
                    success: function (entry_operation, result) {
                        entry_operation.hide_loading();
                        entry_operation.clear();
                        entry_operation.hide();
                        if(result.ret_code == 0){
                            return $('#page-ok').css('display', '-webkit-box').find("#total-money").text(result.margin);
                        }

                        if(result.ret_code == 30047){
                            return Deal_ui.show_entry(result.retry_count, function(){
                                entry_operation.show();
                            })
                        }
                        if(result.ret_code == 30048){
                            return Deal_ui.show_lock('取消', '找回密码', '交易密码已被锁定，请3小时后再试',function(){
                                window.location = '/weixin/sub_pwd_back/?next=/weixin/sub_recharge/'
                            })
                        }
                        if (result.ret_code > 0) {
                            return org.ui.alert(result.message);
                        }


                    },
                    error: function (data) {
                        if (data.status >= 403) {
                            org.ui.alert('服务器繁忙，请稍后再试');
                        }
                    },
                    complete: function () {
                        _self.$recharge.removeAttr('disabled').text("充值");
                    }

                }
                org.ui.confirm("充值金额为" + amount, '确认充值', lib._trade_pwd_seach, data);

            });
        },
        //继续充值
        _close_alt: function(self){
            self.on('click',function(){
                window.location.reload();
            });
        },
        _trade_pwd_seach: function(post_data){
            org.ajax({
                url: '/api/profile/',
                type: 'GET',
                success: function(result){
                    result.trade_pwd_is_set ? lib._trade_pws_operation(true, post_data): lib._trade_pws_operation(false, post_data);
                }
            })

        },
        _trade_pws_operation: function(state, post_data){
            if(state){
                entry_ui()
            }else{
                set_ui()
            }

            function entry_ui(){
                var entry_operation = new Deal({
                    title: '请输入交易密码',
                    sign: '充值金额<br>￥'+ post_data.data.amount,
                    target: $('input[name=password1]'),
                    done : function(pwd){
                        entry_operation.show_loading();
                        post_data.data.trade_pwd = pwd;
                        lib._rechargeSingleStep(entry_operation,post_data)

                    }
                })
                entry_operation.init();
                entry_operation.show();
            }

            var password_1 = null, password_2 = null ;

            function set_ui(){
                var operation_1 = new Deal({
                    title: '设置交易密码',
                    sign: '请设置6位数字作为交易密码',
                    target: $('input[name=password1]'),
                    done : function(pwd){
                        password_1 = pwd;
                        operation_1.clear();
                        operation_1.hide();
                        operation_2();
                    }
                });
                operation_1.init();
                operation_1.show();

                function operation_2(){
                    var operation_2 = new Deal({
                        title: '设置交易密码',
                        sign: '请再次确认交易密码',
                        target: $('input[name=password2]'),
                        done : function(pwd){
                            password_2 = pwd;

                            if(password_2 != password_1){
                                operation_2.clear();
                                operation_2.hide();
                                return Deal_ui.show_alert('error', function(){
                                    set_ui();
                                })
                            }
                            operation_2.show_loading();
                            lib._trade_pws_set(operation_2, password_2, post_data);
                        }
                    });
                    operation_2.init();
                    operation_2.show();
                }
            }

        },
        _trade_pws_set: function(entry_operation, new_trade_pwd, post_data){
            org.ajax({
                url: '/api/trade_pwd/',
                type: 'post',
                data: {
                    action_type: 1,
                    new_trade_pwd: new_trade_pwd
                },
                success: function(result){
                    entry_operation.hide_loading();
                    entry_operation.clear();
                    entry_operation.hide();
                    if(result.ret_code == 0){
                        //Deal_ui.show_alert('success', function(){
                        //    window.location = window.location.href;
                        //},'交易密码设置成功，请牢记！')
                        post_data.data.trade_pwd = new_trade_pwd;
                        lib._rechargeSingleStep(entry_operation,post_data);
                    }

                    if(result.ret_code > 0 ){
                        org.ui.alert(result.message);
                    }
                }
            })
        },
        /**
         * 绑定同卡进出的卡充值
         */
        _rechargeSingleStep: function (operation, data) {
            org.ajax({
                type: 'POST',
                url: '/api/pay/deposit_new/',
                data: data.data,
                beforeSend: function () {
                    data.beforeSend && data.beforeSend()
                },
                success: function (results) {
                    data.success && data.success(operation, results)
                },
                error: function (results) {
                    data.error && data.error(results)
                },
                complete: function () {
                    data.complete && data.complete(operation)
                }
            })
        },
    }
    return {
        init: lib.init
    }
})(org);

org.authentication = (function (org) {
    var lib = {
        isPost: true,
        $fromComplete: $(".from-four-complete"),
        init: function () {
            lib._checkForm();
        },
        _checkForm: function () {
            var formName = ['name', 'id_number'],
                formError = ['.error-name', '.error-card'],
                formSign = ['请输入姓名', '请输入身份证号', '请输入有效身份证'],
                data = {},
                reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/; //身份证正则

            lib.$fromComplete.on('click', function () {
                var isFor = true;
                $('.sign-all').hide();
                $('.check-input').each(function (i) {
                    if (!$(this).val()) {
                        isFor = false;
                        return $(formError[i]).text(formSign[i]).show();
                    } else {
                        if (i === 1 && !reg.test($(this).val())) {
                            isFor = false;
                            return $(formError[i]).text(formSign[2]).show();
                        }
                    }
                    data[formName[i]] = $(this).val();
                });
                isFor && lib._forAuthentication(data)
            });
        },
        _forAuthentication: function (ags) {
            if (lib.isPost) {
                org.ajax({
                    type: 'POST',
                    url: '/api/id_validate/',
                    data: ags,
                    beforeSend: function () {
                        lib.isPost = false;
                        lib.$fromComplete.text("认证中，请等待...");
                    },
                    success: function () {
                        org.ui.alert("实名认证成功!", function () {
                            return window.location.href = '/weixin/account/';
                        });
                    },
                    error: function (xhr) {
                        result = JSON.parse(xhr.responseText);
                        return org.ui.alert(result.message);
                    },
                    complete: function () {
                        lib.isPost = true;
                        lib.$fromComplete.text("完成");
                    }
                })
            }
        }
    };
    return {
        init: lib.init
    }
})(org);

org.bankOneCard = (function(){
    var lib = {
        init : function(){
            lib.listen();
        },
        listen: function(){
            var $set_bank = $('.set-bank'),
                $set_bank_sig  = $('.set-bank-sign'),
                $bank_cancel  = $('.bank-cancel'),
                $bank_confirm =  $('.bank-confirm'),
                $name = $('.name'),
                $no = $('.no');
            var toInvest = $('#to-invest');
            (function(){
                var next = org.getQueryStringByName('next');
                if(toInvest.length > 0 && next != ''){
                    toInvest.attr("href", next).show();
                }
            })();
            $set_bank.on('click', function(){
                var
                    id = $(this).attr('data-id'),
                    no = $(this).attr('data-no'),
                    name = $(this).attr('data-name');

                $set_bank_sig.show();
                $name.text(name);
                $no.text(no.slice(-4));
                $bank_confirm.attr('data-id', id)
            });

            $bank_cancel.on('click', function(){
                $set_bank_sig.hide();
            });

            $bank_confirm.on('click', function(){
                var id = $(this).attr('data-id');
                lib.putBank(id);
            });

        },
        putBank: function(id){
            var $set_bank_sig  = $('.set-bank-sign');
            org.ajax({
                type: 'put',
                url: '/api/pay/the_one_card/',
                data: {
                    card_id: id
                },
                beforeSend: function () {
                    $('.bank-confirm').text('绑定中...').attr('disabled', true);
                },
                success: function (data) {
                    if(data.status_code === 0 ){
                        $set_bank_sig.hide();
                        return org.ui.alert('绑定成功', function(){
                            var url  = window.location.href;
                            window.location.href = url;
                        });
                    }
                },
                error: function (xhr) {
                    $set_bank_sig.hide();
                    var result = JSON.parse(xhr.responseText);
                    return org.ui.alert(result.detail+ '，一个账号只能绑定一张卡')
                },
                complete: function(){
                    $('.bank-confirm').text('立即绑定').removeAttr('disabled');
                }
            })
        }

    }
    return {
        init: lib.init
    }
})();

org.processFirst = (function (org) {
    var lib = {
        $submit: $('button[type=submit]'),
        $name: $('input[name=name]'),
        $idcard: $('input[name=idcard]'),
        init: function () {
            lib._form_logic();
            lib._postData();
        },
        _form_logic: function () {
            var _self = this;

            org.ui.focusInput({
                submit: _self.$submit,
                inputList: [
                    {target: _self.$name, required: true},
                    {target: _self.$idcard, required: true}
                ]
            });
        },

        _postData: function () {
            var _self = this, data = {};
            _self.$submit.on('click', function () {
                data = {
                    name: _self.$name.val(),
                    id_number: _self.$idcard.val()
                };
                _self._check($('.check-list')) && _self._forAuthentication(data)
            });


        },
        _check: function (checklist) {
            var check = true,
                reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;

            checklist.each(function (i) {
                if ($(this).val() == '') {
                    org.ui.showSign($(this).attr('placeholder'));
                    return check = false;
                } else {
                    if (i === 1 && !reg.test($(this).val())) {
                        org.ui.showSign('请输入正确的身份证号');
                        return check = false;
                    }
                }
            });

            return check
        },
        _forAuthentication: function (postdata) {
            org.ajax({
                type: 'POST',
                url: '/api/id_validate/',
                data: postdata,
                beforeSend: function () {
                    lib.$submit.attr('disabled', true).text("认证中，请等待...");
                },
                success: function (data) {
                    if(!data.validate == 'true') return org.ui.alert('认证失败，请重试');
                    //org.ui.alert("实名认证成功!",function(){
                    //    window.location.href = '/weixin/sub_regist_second/';
                    //});
                    //org.ui.alert("实名认证成功!",{url:'/weixin/sub_regist_second/'});
                    $('.sign-main').css('display','-webkit-box');
                },
                error: function (xhr) {
                    result = JSON.parse(xhr.responseText);
                    if(result.error_number == 8){
                        //org.ui.alert(result.message,function(){
                        //   window.location.href = '/weixin/sub_list/';
                        //});
                        $('.sign-main-error').css('display','-webkit-box').find(".sign-tit").html(result.message);
                    }else{
                        return org.ui.alert(result.message);
                    }

                },
                complete: function () {
                    lib.$submit.removeAttr('disabled').text("实名认证");
                }
            })
        }
    }
    return {
        init: lib.init
    }
})(org);

org.processSecond = (function (org) {
    var lib = {
        $submit: $('button[type=submit]'),
        $bank: $('select[name=bank]'),
        $bankcard: $('input[name=bankcard]'),
        $bankphone: $('input[name=bankphone]'),
        $validation: $('input[name=validation]'),
        $money: $('input[name=money]'),
        init: function () {
            lib._init_select();
            lib.form_logic();
            lib._validation();
            lib._submit();
        },

        _format_limit: function(amount){
            var money = amount, reg = /^\d{5,}$/, reg2 = /^\d{4}$/;
            if(reg.test(amount)){
                 return money = amount.replace('0000','') + '万'
            }
            if(reg2.test(amount)){
                return money = amount.replace('000','') + '千'
            }
        },
        _limit_style: function(data){
            var _self = this, $limitItem = $('.limit-bank-item'), list = '';

            for(var i =0; i< data.length;i++){
                list += "<div class='limit-bank-list'>"
                list += "<div class='limit-list-dec'> "
                list += "<div class='bank-name'>"+data[i].name+"</div>";
                list += "<div class='bank-limit'>首次限额"+_self._format_limit(data[i].first_one)+"/单笔限额"+_self._format_limit(data[i].first_one)+"/日限额"+_self._format_limit(data[i].second_day)+"</div>";
                list += "</div>"
                list += "<div class='limit-list-icon "+data[i].bank_id+"'></div>"
                list += "</div>"
            }
            $limitItem.html(list)
        },
        _init_select: function(){
            if(localStorage.getItem('bank')){
                var content = JSON.parse(localStorage.getItem('bank'));
                lib.$bank.append(appendBanks(content));
                lib._limit_style(content)
            }
            org.ajax({
                type: 'POST',
                url: '/api/bank/list_new/',
                success: function (results) {
                    if (results.ret_code === 0) {
                        lib.$bank.append(appendBanks(results.banks));
                        var content = JSON.stringify(results.banks);
                        window.localStorage.setItem('bank', content);
                    } else {

                        return org.ui.alert(results.message);
                    }
                },
                error: function (data) {
                    console.log(data)
                }
            })

            function appendBanks(banks) {
                var str = ''
                for (var bank in banks) {
                    str += "<option value =" + banks[bank].gate_id + " > " + banks[bank].name + "</option>"
                }
                return str
            }
        },
        form_logic: function () {
            var _self = this;
            org.ui.focusInput({
                submit: _self.$submit,
                inputList: [
                    {target: _self.$bankcard, required: true},
                    {target: _self.$bankphone, required: true},
                    {target: _self.$validation, required: true},
                    {target: _self.$money, required: true}
                ],
                otherTarget: [{target: _self.$bank, required: true}]
            });

            org.ui.focusInput({
                submit: $('.regist-validation'),
                inputList: [
                    {target: _self.$bankcard, required: true},
                    {target: _self.$bankphone, required: true},
                    {target: _self.$money, required: true}
                ],
                otherTarget: [{target: _self.$bank, required: true}],
                submitStyle: {
                    'disabledBg': '#ccc',
                    'activeBg': '#50b143',
                }

            });

            var addClass = _self.$bank.attr('data-icon'),
                $target = $('.' + _self.$bank.attr('data-target2'));

            _self.$bank.change(function () {
                if ($(this).val() == '') {
                    $target.addClass(addClass).removeClass(addClass + '-active');
                } else {
                    $target.addClass(addClass + '-active').removeClass(addClass);
                }
                _self.$bankcard.trigger('input')
            });

        },
        _validation: function () {
            var _self = this,
                re = new RegExp(/^(12[0-9]|13[0-9]|15[0123456789]|18[0123456789]|14[57]|17[0678])[0-9]{8}$/),
                $validationBtn = $('.regist-validation');

            $validationBtn.on('click', function () {
                var count = 60, intervalId; //定时器

                if (_self.$bankcard.val().length < 10) {
                    return org.ui.alert('银行卡号不正确');
                }

                if (!re.test(_self.$bankphone.val())) {
                    return org.ui.alert('请填写正确手机号');
                }

                $(this).attr('disabled', 'disabled').css('background', '#ccc')
                //倒计时
                var timerFunction = function () {
                    if (count >= 1) {
                        count--;
                        return $validationBtn.text(count + '秒后可重发');
                    } else {
                        clearInterval(intervalId);
                        $validationBtn.text('重新获取').removeAttr('disabled').css('background', '#50b143');
                        return;
                    }
                };
                var money = function(){
                    if(_self.$money.length == 0){
                        return 0.01
                    }else{
                        return _self.$money.val()
                    }
                };
                org.ajax({
                    type: 'POST',
                    url: '/api/pay/deposit_new/',
                    data: {
                        card_no: _self.$bankcard.val(),
                        gate_id: _self.$bank.val(),
                        phone: _self.$bankphone.val(),
                        amount: money()
                    },
                    success: function (data) {
                        if (data.ret_code > 0) {
                            clearInterval(intervalId);
                            $validationBtn.text('重新获取').removeAttr('disabled').css('background', '#50b143');
                            return org.ui.alert(data.message);
                        } else {
                            $("input[name='order_id']").val(data.order_id);
                            $("input[name='token']").val(data.token);
                        }
                    },
                    error: function (data) {
                        clearInterval(intervalId);
                        $validationBtn.text('重新获取').removeAttr('disabled').css('background', '#50b143')
                        return org.ui.alert(data);
                    }
                })
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            })
        },
        _submit: function () {
            var _self = this;

            _self.$submit.on('click', function () {
                var check_recharge = $(this).attr('data-recharge');
                if(check_recharge == 'true'){
                    org.ui.confirm("充值金额为" + _self.$money.val(), '确认充值', recharge, {firstRecharge: true});
                }else{
                    recharge({firstRecharge: false});
                }

            });

            function recharge(check) {
                org.ajax({
                    type: 'POST',
                    url: '/api/pay/cnp/dynnum_new/',
                    data: {
                        phone: _self.$bankphone.val(),
                        vcode: _self.$validation.val(),
                        order_id: $('input[name=order_id]').val(),
                        token: $('input[name=token]').val(),
                        set_the_one_card: true
                    },
                    beforeSend: function () {
                        if(check.firstRecharge){
                            _self.$submit.attr('disabled', 'disabled').text('充值中...');
                        }else{
                            _self.$submit.attr('disabled', 'disabled').text('绑卡中...');
                        }

                    },
                    success: function (data) {
                        if (data.ret_code > 0) {
                            return org.ui.alert(data.message);
                        } else {
                            if(check.firstRecharge){
                                $('.sign-main').css('display', '-webkit-box').find(".balance-sign").text(data.amount);
                            }else{
                                return org.ui.alert('绑卡成功！');
                            }

                        }
                    },
                    error: function(result){
                        var data = JSON.parse(result.responseText);
                        return org.ui.alert(data.detail);
                    },
                    complete: function () {
                        if(check.firstRecharge){
                            _self.$submit.removeAttr('disabled').text('绑卡并充值');
                        }else{
                            _self.$submit.removeAttr('disabled').text('立即绑卡');
                        }

                    }
                })
            }

        }
    }
    return {
        init: lib.init
    }
})(org);

org.trade_back = (function (org) {
    var lib = {
        $submit : $('button[type=submit]'),
        $id_number : $('input[name=id_number]'),
        $bankcard : $('input[name=bankcard]'),
        $cardname : $('input[name=cardname]'),
        init: function () {
            lib.the_one_card();
            lib.listen_input();
        },
        /**
         * 判断有没有同卡进出的卡
         */
        the_one_card: function () {
            var _self = this;
            org.ajax({
                type: 'get',
                url: '/api/pay/the_one_card/',
                success: function (data) {
                    //同卡进出
                    var CARDNAME = data.bank.name;
                    var CARDNO = data.no.slice(-4);
                    $('.bank-name').html(CARDNAME);
                    $('.bank-card').html(CARDNO);
                    lib.$bankcard.attr('placeholder', "**"+ CARDNO +"（请输入完整卡号）");
                    $('.trade-warp').show();
                },
                error: function (data) {
                    //没有同卡进出
                    $('.unbankcard').show()
                },
                complete: function(){
                    $('.recharge-loding').hide()
                }
            })
        },
        listen_input: function(){
            var _self = this;
            org.ui.focusInput({
                submit: _self.$submit,
                inputList: [
                    {target: _self.$id_number, required: true},
                    {target: _self.$bankcard, required: true},
                    {target: _self.$cardname, required: true}
                ]
            });

            _self.$submit.on('click', function(){
                _self._trade_pws_operation()
            })

        },
        _trade_pws_operation: function(){

            var password_1 = null, password_2 = null ;
            function set_ui(){
                var operation_1 = new Deal({
                    title: '请输入新交易密码',
                    sign: '请设置6位数字作为新交易密码',
                    target: $('input[name=password1]'),
                    done : function(pwd){
                        password_1 = pwd;
                        operation_1.clear();
                        operation_1.hide();
                        operation_2();
                    }
                })
                operation_1.init();
                operation_1.show();

                function operation_2(){
                    var operation_2 = new Deal({
                        title: '请输入新交易密码',
                        sign: '请再次确认新交易密码',
                        target: $('input[name=password2]'),
                        done : function(pwd){
                            password_2 = pwd;

                            if(password_2 != password_1){
                                operation_2.clear();
                                operation_2.hide();
                                return Deal_ui.show_alert('error', function(){
                                    set_ui()
                                })
                            }
                            operation_2.show_loading();
                            lib._trade_pws_set(operation_2, password_2)
                        }
                    });
                    operation_2.init();
                    operation_2.show();
                }
            }

            set_ui()

        },
        _trade_pws_set: function(operation, new_trade_pwd){
            var _self = this;
            var card_id = _self.$bankcard.val(),
                citizen_id = _self.$id_number.val();
            org.ajax({
                url: '/api/trade_pwd/',
                type: 'post',
                data: {
                    action_type: 3,
                    new_trade_pwd: new_trade_pwd,
                    card_id : card_id,
                    citizen_id: citizen_id
                },
                success: function(result){
                    var next = org.getQueryStringByName('next') == '' ? '/weixin/sub_list/' : org.getQueryStringByName('next');
                    if(result.ret_code == 0){
                        Deal_ui.show_alert('success', function(){
                            window.location = next;
                        })
                    }

                    if(result.ret_code > 0 ){
                        org.ui.alert(result.message);
                    }
                },
                complete: function(){
                    operation.hide_loading();
                    operation.clear();

                    operation.hide();
                }
            })
        },
    };
    return {
        init: lib.init
    }
})(org);

(function(){
    function Deal(ops){
        this.title = ops.title;
        this.sign = ops.sign;
        this.callback = ops.done;
        this.$input = ops.target;
        this.$body =  $('.tran-warp');
        this.$blue = this.$body.find('span.blue');
        this.$digt =  $('.six-digt-password');
        this.$close = $('.tran-close');
        this.blue_width = null;
        this.password = null;
        this.reCreate();
    }
    Deal.prototype.init = function(){
        var _self = this;

        $('.head-title').html(this.title);
        $('.tran-sign').html(this.sign);

        this.$close.on('click', function(){
            _self.hide()
        });

        this.$digt.on('click', function(e){
            _self.$input.focus();
            _self.decide('click');
            e.stopPropagation();
        });

        this.$input.on('input', function(){
            $('.circle').hide();
            _self.decide('input')
        });

       $(document).on('click', function(){
           _self.$digt.find('i').removeClass('active');
           _self.hide_blue();
       });
    }
    Deal.prototype.reCreate = function(){
        this.$input.off('input');
        this.$close.off('click');
        $(document).off('click');
        this.$digt.off('click').find('i').removeClass('active');
        $('.six-digt-password i ').find('.circle').hide();
    }
    Deal.prototype.clear = function(){
        this.$input.val('');
        this.$digt.find('i').removeClass('active');
        $('.six-digt-password i ').find('.circle').hide();
    }
    Deal.prototype.decide = function(type){
        var value_num = this.$input.val().length;

        for(var i = 0; i< value_num; i++){
            $('.six-digt-password i ').eq(i).find('.circle').show();
        }
        this.password = this.$input.val();
        this.show_blue();
        this.move(value_num, type);
    }
    Deal.prototype.move = function(index, type){

        var move_space = this.blue_width * index;
        if(index == 5){
            this.$blue.width(this.$digt.width()-move_space);
        }else{
            this.$blue.width(this.blue_width);
        }
        if(index == 6){
            move_space = this.blue_width * 5 ;
        }
        this.$blue.animate({
            'translate3d': move_space + "px, 0 , 0"
        },0);

        if(index == 6){
            this.$digt.find('i').removeClass('active');
            if(type == 'input'){
                this.hide_blue();
                this.$input.blur();
                this.done()
            }
            return
        }

        this.$digt.find('i').eq(index).addClass('active').siblings('i').removeClass('active')
    }
    Deal.prototype.show_blue = function(){
        return this.$blue.css('visibility', 'visible')
    }
    Deal.prototype.hide_blue = function(){
        return this.$blue.css('visibility', 'hidden')
    }
    Deal.prototype.show = function(){
        this.$body.show();
        this.blue_width = Math.floor(this.$blue.width());
        return ;
    }
    Deal.prototype.hide = function(){
        return this.$body.hide();
    }
    Deal.prototype.show_loading = function(){
        return $('.tran-loading').css('display','-webkit-box')
    }
    Deal.prototype.hide_loading = function(){
        return $('.tran-loading').css('display','none')
    }
    Deal.prototype.done = function(){
        return this.callback && this.callback(this.password);
    }

    Deal_ui = {
        show_alert: function(state, callback, state_message){
            $('.tran-alert-error').show().find('.'+state).show().siblings().hide();
            if(state_message)  $('.tran-alert-error').show().find('.'+state).find('p').html(state_message);
            $('.tran-alert-error').find('.alert-bottom').one('click', function(){
                $('.tran-alert-error').hide();
                callback && callback();
            })
            return
        },
        show_entry: function(count, callback){
            $('.tran-alert-entry').show().find('.count_pwd').html(count);
            $('.tran-alert-entry').find('.alert-bottom').one('click', function(){
                $('.tran-alert-entry').hide();
                callback && callback();
            });
            return
        },
        show_lock: function(left,right,dec, callback){
            $('.tran-alert-lock').show();
            $('.lock-close').html(left).one('click', function(){
                $('.tran-alert-lock').hide()

            });
            $('.tran-alert-lock').find('.tran-dec-entry').html(dec);
            $('.lock-back').html(right).one('click', function(){
                callback && callback();
            })
        }


    }
    window.Deal = Deal;
    window.Deal_ui = Deal_ui;
})();


org.received_ui = (function(){
    var slide = function(data){
        var slide = "<div class='swiper-slide received-slide'>"
            slide += "<div class='received-slide-date'>"+data.term_date.slice(0,4)+"年"+data.term_date.slice(5,7)+"月</div>"
            slide += "<div class='received-slide-data'>";
            slide += "<div class='received-data-list'>";
            slide += "<span class='received-left-center'>"
            slide += "<div class='data-name'>回款总额(元)</div>"
            if(data.total_sum == 0){
                slide += "<div class='data-value'>0.00</div>"
            }else{
                slide += "<div class='data-value'>"+data.total_sum +"</div>"
            }
            slide += "</span>"
            slide += "</div>"
            slide += "<div class='received-data-list'>";
            slide += "<span class='received-left-center'>"
            slide += "<div class='data-name'>回款笔数</div>"
            if(data.term_date_count == 0){
                slide += "<div class='data-value'>0.00</div>"
            }else{
                slide += "<div class='data-value'>"+data.term_date_count +"</div>"
            }
            slide += "</span>"
            slide += "</div>"
            slide += "</div>"
            slide += "</div>"

        return slide
    }

    var list = function(data){
        var list = "<a href='/weixin/received/detail/?productId="+data.product_id+"' class='received-list'>";
            list += "<div class='list-head-warp'>";
            list += "<div class='list-head arrow'>";
            list += "<div class='head-space'>&nbsp&nbsp</div>"
            list += "<span class='head-name'>"+data.product_name+"</span>"
            list += "<span class='head-process'>"+data.term+"/"+data.term_total+"</span>"
            list += "</div></div>";

            list += "<div class='list-cont'>";
            list += "<div class='list-flex'>";
            list += "<div class='cont-grey-2'>"+data.term_date.slice(0,10)+"</div>";
            list += "<div class='cont-grey-1'>回款日期</div>";
            list += "</div>";
            list += "<div class='list-flex'>";
            list += "<div class='cont-red'>"+data.principal+"</div>";
            list += "<div class='cont-grey-1'>本(元)</div>";
            list += "</div>";

            list += "<div class='list-flex'>";
            list += "<div class='cont-red'>"+data.total_interest+"</div>";
            list += "<div class='cont-grey-1'>息(元)</div>";
            list += "</div>";

            list += "<div class='list-flex'>";
            list += "<div class='cont-grey-2'>"+data.settlement_status+"</div>";
            if(data.settlement_status == '提前回款'){
                list += "<div class='cont-grey-1'>"+data.settlement_time.slice(0,10)+"</div>";
            }
            list += "</div>";
            list += "</div>";

            list += "</div></a>"

        return list

    }

    var detail = function(data){
        var detail = "<div class='list-head-warp'>";
            detail += "<div class='list-head'>";
            detail += "<div class='head-space'>&nbsp&nbsp</div>";
            detail += "<span class='head-name head-allshow'>"+data.equity_product_short_name+"</span>";
            detail += "</div></div>";

            detail += "<div class='list-nav'>";
            detail += "<ul><li class='item-date'>时间</li><li>本金(元)</li><li>利息(元)</li><li class='item-count'>总计(元)</li></ul>";
            detail += "</div>";
            detail += "<div class='detail-space-grep'></div>";

            for(var i=0; i< data.amortization_record.length;i++){

                detail += "<div class='detail-list'>";
                detail += "<div class='detail-item item-date'>"+data.amortization_record[i].amortization_term_date.slice(0,10)+"</div>";
                detail += "<div class='detail-item'>"+data.amortization_record[i].amortization_principal+"</div>";
                detail += "<div class='detail-item'>" + data.amortization_record[i].amortization_amount_interest;
                if(data.amortization_record[i].amortization_coupon_interest > 0){
                    detail += "<span>+</span><span class='blue-text'>"+data.amortization_record[i].amortization_coupon_interest+"</span><span class='blue-sign'>加息</span>";
                }
                detail += "</div>";
                detail += "<div class= 'detail-item item-count'>"+data.amortization_record[i].amortization_amount+"</div>";
                if(data.amortization_record[i].amortization_status== '提前回款' || data.amortization_record[i].amortization_status== '已回款'){
                    detail += "<div class= 'repayment-icon'></div>";
                }
                detail += "</div>";
            }


        return detail;
    }

    return {
        slide: slide,
        list: list,
        detail: detail
    }
})();
org.received_all = (function(){
    var lib = {
        init: function(){
            lib.init_operation()

        },
        init_operation:function(){
            var _self = this;

            function style(data){
                var slide = [], INDEX = null;
                for(var i =0; i< data.month_group.length; i++){
                    if(data.current_month == data.month_group[i].term_date){
                        INDEX = i;
                    }
                    slide.push(org.received_ui.slide(data.month_group[i]))
                }
                swiper_m.appendSlide(slide);
                swiper_m.slideTo(INDEX, 150, false);
                 _self.list_style(data)
                $('.received-loding').hide()
            }

            var swiper_m = new Swiper('.swiper-container', {
                direction: 'horizontal',
                loop: false,
                slidesPerView: 1.21,
                centeredSlides: true,
                paginationClickable: true,
                spaceBetween: 30,
                onSlideChangeStart:function(swiper){
                    var slide_index = swiper.activeIndex;
                    var target = $('.swiper-slide').eq(slide_index).find('.received-slide-date').text();
                    var year = target.slice(0,4);
                    var month = target.slice(5,-1);
                    $('.received-loading-warp').show()
                    _self.fetch({ year: year,  month: month}, _self.list_style)
                }
            });

            _self.fetch({ year: '',  month: ''}, style);

        },
        list_style: function(data){
            var slide = [],
                $item = $('.receive-body'),
                $default =$('.received-default');
            if(data.data.length === 0){
                $item.html('');
                $default.show();
                return
            }
            for(var i =0; i< data.data.length; i++){
                slide.push(org.received_ui.list(data.data[i]))
            }
            $default.hide();
            $item.html(slide.join(''))
            $('.received-loading-warp').hide()

        },
        fetch: function(data, callback){
            org.ajax({
                url: '/api/m/repayment_plan/month/',
                type: 'POST',
                data: data,
                success:function(data){
                    callback && callback(data)
                }
            })
        }

    }

    return {
        init : lib.init
    }
})();

org.received_month = (function(){
    var lib = {
        page: 1,
        num: 10,
        init: function(){
            var
                _self = lib;

            var get_data = function(callback){
                _self.fetch({
                    page: _self.page,
                    num: _self.num
                },callback)
            }

            get_data(function(){
                $('.received-loding').hide()
            });

            $('.received-more').on('click', function(){
               get_data()
            })
        },
        init_style:function(data){
            var slide = [],
                $item = $('.received-item');
            for(var i =0; i< data.data.length; i++){
                slide.push(org.received_ui.list(data.data[i]))
            }
            $item.append(slide.join(''))
        },
        fetch: function(data, callback){
            var _self = this;
            org.ajax({
                url: '/api/m/repayment_plan/all/',
                type: 'POST',
                data: data,
                beforeSend: function(){
                    $('.received-more').attr('disabled',true).html('加载中，请稍后...')
                },
                success:function(data){
                    if(data.count === 0 ){
                        $('.received-default').show()
                    }
                    if(data.count - data.page > 0 ){
                        $('.received-more').show()
                    }else{
                        $('.received-more').hide()
                    }
                    _self.page = _self.page + 1;

                    _self.init_style(data)
                    callback && callback(data)

                },
                complete: function(){
                    $('.received-more').removeAttr('disabled').html('加载更多')
                }

            })
        }
    }

    return {
        init : lib.init
    }
})();

org.received_detail = (function(){
    var lib = {
        init: function(){
            var
                _self = lib;
            var product_id  = org.getQueryStringByName('productId')
            _self.fetch(product_id);
        },
        init_style:function(data){
            var slide = [],
                $item = $('.received-list');
            slide.push(org.received_ui.detail(data));
            $item.append(slide.join(''));
            $('.received-loding').hide();
        },
        fetch: function(product_id){
            var _self = this;

            org.ajax({
                url: '/api/home/p2p/amortization/'+product_id,
                type: 'get',
                success:function(data){
                    _self.init_style(data);
                }
            })
        }
    }

    return {
        init : lib.init
    }
})();

//关闭页面，返回微信
function closePage(){
    if(typeof (WeixinJSBridge) != 'undefined'){
        WeixinJSBridge.call('closeWindow');
    }else{
        window.close();
    }
}

//签到
org.checkIn = (function(org){
    var lib = {
        giftOk: true,
        altDom: $(".check-in-alert-layout"),
        init: function(){
            lib.getGift();
            lib.closeAlt();
            lib.loadInit();
        },
        loadInit: function(){
            org.ajax({
                url: "/weixin/sign_info/",
                type: "GET",
                dataType: "json",
                success: function(data){
                    var result = data.data;
                    console.log(result,result.sign_in);
                    var giftNum = result.sign_in.nextDayNote,//礼物天数
                        nowDay = result.sign_in.current_day,
                        nextNum = giftNum - nowDay,
                        className = '',
                        html = '';
                    var checkIn = $(".checkin-op-status"),
                        checkIn_detail = checkIn.find(".op-dec-detail"),
                        checkShare = $(".checkin-op-share");
                    if(!result.sign_in.status){//签到
                        checkIn.find("div.op-dec-title").text("今日未签到");
                        checkIn_detail.hide();
                    }else{
                        checkIn_detail.text(result.sign_in.amount);
                    }
                    if(result.share.status){//分享
                        checkShare.addClass("checkin-share-ok");
                        checkShare.find(".op-detail-orange").text(result.sign_in.amount);
                    }
                    for(var i=1; i<=giftNum; i++){
                        if(nowDay === giftNum){
                            className = 'active-did active-gift active-doing';
                        }else{
                            if(i < nowDay){
                                className = 'active-did';
                            }else if(i === nowDay){
                                className = 'active-did active-doing';
                            }else if(i === giftNum){
                                className = 'active-gift';
                            }else{
                                className = '';
                            }
                        }
                        html += '<div class="flag-items '+ className +'">' +
                                    '<div class="circle-item-warp">' +
                                        '<div class="circle-item">' +
                                            '<div class="circle-min"></div>'+
                                            '<div class="circle-animate"></div>'+
                                            '<div class="check-in-flag"></div>'+
                                        '</div>'+
                                    '</div>' +
                                    '<div class="text-item">'+ i +'天</div>' +
                                '</div>';
                    }
                    $("div.check-in-flag-lists").html(html);
                    $("#giftDay").text(nextNum);
                }
            });
        },
        closeAlt: function(){
            $(".close-alert").on("click",function(){
                $(this).parents(".check-in-alert-layout").hide();
            });
        },
        getGift: function(){
            var giftOk = lib.giftOk;
            $(".active-gift.active-did").on("touchstart",function(){
                var self = $(this);
                if(self.hasClass("active-gift-open")){
                    return;
                }
                if(giftOk){
                    giftOk = false;
                    self.addClass("active-gift-open");
                    if(lib.altDom.hasClass("check-in-share")){
                        lib.altDom.removeClass("check-in-share");
                    }
                    lib.altDom.show();
                }
            });
        },
        shareFn: function(){
            if(!lib.altDom.hasClass("check-in-share")){
                lib.altDom.addClass("check-in-share");
            }
            lib.altDom.show();
        },
        shareOk: function(){
            var share = {shareLink:'', shareMainTit:'网利宝天天送我钱，不想要都不行～朋友们快来领啊～', shareBody:'', success:shareFn};
            org.detail.share(share);
        }
    };
    return {
        init: lib.init
    }
})(org);

;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if (src && src.indexOf(org.scriptName) > 0) {
            if ($(this).attr('data-init') && org[$(this).attr('data-init')]) {
                org[$(this).attr('data-init')].init();
            }
        }
    });
    org.detail.init();//下载、微信分享

    $("#no-unbind,.back-weixin").addClass("clickOk").click(function(){
        closePage();
    });

    function timeFun(){//倒计时跳转
      var numDom = $("#times-box");
      var num = parseInt(numDom.text());
      var timeSet = setInterval(function(){
        if(num <= 0){
          clearInterval(timeSet);
          closePage();
          return;
        }
        num --;
        numDom.text(num+"秒");
      },1000);
    }
    window.onload = function(){
        timeFun();
        $("#unbind").addClass("clickOk");
    };

    var unbindf = false;
    function unbingFun(){
        unbindf = true;
        //var openid = $("#openid").val();
        org.ajax({
            type: "post",
            url: "/weixin/api/unbind/",
            //data: {"openid":openid},
            dataType: "json",
            success: function (data) {
                //console.log(data);
                unbindf = false;
                window.location.href="/weixin/jump_page/?message=您已经解除绑定";
            }
        });
    }
    //解除绑定
    $("#unbind").click(function(){
        var self = $(this);
        if(unbindf){
            self.text("正在解除……");
            self.off("click");
            self.addClass("unbings")
        }else{
            self.text("解除绑定");
            self.on("click",unbingFun());
            self.removeClass("unbings")
        }
    });


    //关闭底部
    $("#footer-down").on("click",".down-close",function(){
        $("#footer-down").hide();
    });

    function btnAnimate(self,tp,k){//抽奖动画
        var arrStr = ["终于等到你还好我没放弃","人品大爆发！"];
        var errorStr = ['太可惜了，你竟然与大奖擦肩而过','天苍苍，野茫茫，中奖的希望太渺茫','你和大奖只是一根头发的距离','奖品何时有，把酒问青天？','据说心灵纯洁的人中奖几率更高'];
        var btns = tp.find(".award-item");
        var i = 0;
        var num = 0;
        var alt = $("#alt-box");
        var altAwardP = alt.find("#alt-award-p");
        var altCont = alt.find(".alt-cont");
        var altPro = alt.find("#alt-promot");
        var sleep = 60;
        function setAn(){
            btns.eq(i).addClass("awards-now").siblings(".award-item").removeClass("awards-now");
            if(i === k && num > 1){
                clearInterval(setAnimate);
                setTimeout(function(){
                    $("#page-bg").show();
                    if(k === 0){
                        altPro.text(errorStr[Math.floor(Math.random()*5)]);
                        altAwardP.html('');
                        altCont.removeClass("mt");
                    }else{
                        altPro.text(arrStr[Math.floor(Math.random()*2)]);
                        altAwardP.html('<span id="alt-award" class="alt-award">'+btns.eq(i-1).text()+'</span>已在您的账户中');
                        altCont.addClass("mt");
                    }
                    //altCont.find(".alt-btn").html('<span class="alt-award red-btns close-box">继续攒人品</span>');
                    self.removeClass("had-click");
                    alt.show();
                },sleep);
            }
            if(i >= btns.length){
                num ++;
                clearInterval(setAnimate);
                i = 0;
                setAnimate = setInterval(setAn,sleep);
            }else{
              i ++;
            }
        }
        var setAnimate = setInterval(function(){
            setAn();
        },sleep);
    }
    var awardBtn = true;
    //立即抽奖
    $("#award-btn").click(function(){
        var self = $(this);
        var isNum = goods;
        var nowNum = 0;
        var awardAction = "ENTER_WEB_PAGE";
        var altDom = $("#alt-box");
        if(awardsNum === 0){
            $("#page-bg").show();
            altDom.find("#alt-promot").text("大奖明天见，网利宝天天见。");
            altDom.find("#alt-award-p").text("您今天已经抽奖，明天再来碰运气吧");
            altDom.find(".alt-cont").addClass("mt");
            altDom.find(".alt-btn").html('<span class="alt-award red-btns close-box">知道了</span>');
            altDom.show();
            self.addClass("had-click");
            return;
        }
        if(awardBtn){
            awardBtn = false;
            self.addClass("had-click");
            if(awardsNum === 2){
                awardAction = 'GET_REWARD';
                nowNum = isAwards(isNum);
            }else{
                awardAction = 'IGNORE';
                nowNum = 0;
            }
        }else{
            return;
        }

        org.awardEvent(awardAction,function(d){ //ajax
            //console.log(d);
            $("#sub-award-num").text(d.left);
            isNum = parseFloat(d.amount);
        });
        var awards = self.parents("div.award-handle-box").siblings("div.award-btn-box");

        btnAnimate(self,awards,nowNum);//执行动画
    });
    //关闭弹层
    $("#alt-box").on("click",".close-box",function(){
        $(this).parents("#alt-box").hide();
        $("#page-bg").hide();
        awardBtn = true;
    });

    //抽奖活动 显示规则
    $("#show-alt-rule").click(function(){
        $("#sub-body-rule").show();
    });
    $("#close-this").click(function(){
        $(this).parents("#sub-body-rule").hide();
    });
})(org);

//页面加载完成 添加class
function onLoadClass(){
    var html = $("html");
    if(html.height() <= $(window).height()){
        html.addClass("sub-height");
    }else{
        html.removeClass("sub-height");
    }
}
function getCode(){//得到用户信息的二维码
    var phone = org.getQueryStringByName('phone');
    var original_id = document.getElementById("original_id").value;
    var code = document.getElementById("weixin_code").value;
    org.ajax({
        type: "GET",
        url: "/weixin/api/generate/qr_scene_ticket/",
        data: {"original_id":original_id, "code": code},//c:gh_32e9dc3fab8e, w:gh_f758af6347b6;code:微信关注渠道
        success: function (data) {
            $("#sub-code").html("<img src='"+ data.qrcode_url + "' />");
        },
        error: function(){
            window.location.href="/weixin/jump_page/?message=出错了";
        }
    });
}
function isIphone(id){
    var ipad = navigator.userAgent.match(/(iPad).*OS\s([\d_]+)/) ? true : false,
        iphone = !ipad && navigator.userAgent.match(/(iPhone\sOS)\s([\d_]+)/) ? true : false,
        ios = ipad || iphone;
    if (ios) {
      document.getElementById(id).style.display = 'block';
    }
}

function isAwards(k){//判断抽奖是第几项
    var is = 0;
    switch(k){
        case 0.2:
            is = 1;
            break;
        case 0.3:
            is = 2;
            break;
        case 0.4:
            is = 3;
            break;
        case 1:
            is = 4;
            break;
        case 1.5:
            is = 5;
            break;
        case 25:
            is = 6;
            break;
        case 2:
            is = 7;
            break;
        case 6:
            is = 8;
            break;
        case 10:
            is = 9;
            break;
        default :
            is = 0;
            break;
    }
    return is;
}

var awardsNum = 0,
    goods = '';
org.awardEvent = (function(org){ //微信抽奖
    var awardFun = function(obj, fn){
        org.ajax({
            type: "post",
            url: '/api/weixin/distribute/redpack/',
            dataType: 'json',
            data: {"action": obj,"openid": $("#openid").val()},
            success: function(data){
                fn(data);
                awardsNum = data.left;
                goods = parseFloat(data.amount);
            },
            error: function(){}
        });
    };
    return awardFun;
})(org);


