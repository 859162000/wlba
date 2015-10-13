var Zepto=function(){function L(t){return null==t?String(t):j[S.call(t)]||"object"}function Z(t){return"function"==L(t)}function _(t){return null!=t&&t==t.window}function $(t){return null!=t&&t.nodeType==t.DOCUMENT_NODE}function D(t){return"object"==L(t)}function M(t){return D(t)&&!_(t)&&Object.getPrototypeOf(t)==Object.prototype}function R(t){return"number"==typeof t.length}function k(t){return s.call(t,function(t){return null!=t})}function z(t){return t.length>0?n.fn.concat.apply([],t):t}function F(t){return t.replace(/::/g,"/").replace(/([A-Z]+)([A-Z][a-z])/g,"$1_$2").replace(/([a-z\d])([A-Z])/g,"$1_$2").replace(/_/g,"-").toLowerCase()}function q(t){return t in f?f[t]:f[t]=new RegExp("(^|\\s)"+t+"(\\s|$)")}function H(t,e){return"number"!=typeof e||c[F(t)]?e:e+"px"}function I(t){var e,n;return u[t]||(e=a.createElement(t),a.body.appendChild(e),n=getComputedStyle(e,"").getPropertyValue("display"),e.parentNode.removeChild(e),"none"==n&&(n="block"),u[t]=n),u[t]}function V(t){return"children" in t?o.call(t.children):n.map(t.childNodes,function(t){return 1==t.nodeType?t:void 0})}function B(n,i,r){for(e in i){r&&(M(i[e])||A(i[e]))?(M(i[e])&&!M(n[e])&&(n[e]={}),A(i[e])&&!A(n[e])&&(n[e]=[]),B(n[e],i[e],r)):i[e]!==t&&(n[e]=i[e])}}function U(t,e){return null==e?n(t):n(t).filter(e)}function J(t,e,n,i){return Z(e)?e.call(t,n,i):e}function X(t,e,n){null==n?t.removeAttribute(e):t.setAttribute(e,n)}function W(e,n){var i=e.className||"",r=i&&i.baseVal!==t;return n===t?r?i.baseVal:i:void (r?i.baseVal=n:e.className=n)}function Y(t){try{return t?"true"==t||("false"==t?!1:"null"==t?null:+t+""==t?+t:/^[\[\{]/.test(t)?n.parseJSON(t):t):t}catch(e){return t}}function G(t,e){e(t);for(var n=0,i=t.childNodes.length;i>n;n++){G(t.childNodes[n],e)}}var t,e,n,i,C,N,r=[],o=r.slice,s=r.filter,a=window.document,u={},f={},c={"column-count":1,columns:1,"font-weight":1,"line-height":1,opacity:1,"z-index":1,zoom:1},l=/^\s*<(\w+|!)[^>]*>/,h=/^<(\w+)\s*\/?>(?:<\/\1>|)$/,p=/<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/gi,d=/^(?:body|html)$/i,m=/([A-Z])/g,g=["val","css","html","text","data","width","height","offset"],v=["after","prepend","before","append"],y=a.createElement("table"),x=a.createElement("tr"),b={tr:a.createElement("tbody"),tbody:y,thead:y,tfoot:y,td:x,th:x,"*":a.createElement("div")},w=/complete|loaded|interactive/,E=/^[\w-]*$/,j={},S=j.toString,T={},O=a.createElement("div"),P={tabindex:"tabIndex",readonly:"readOnly","for":"htmlFor","class":"className",maxlength:"maxLength",cellspacing:"cellSpacing",cellpadding:"cellPadding",rowspan:"rowSpan",colspan:"colSpan",usemap:"useMap",frameborder:"frameBorder",contenteditable:"contentEditable"},A=Array.isArray||function(t){return t instanceof Array};return T.matches=function(t,e){if(!e||!t||1!==t.nodeType){return !1}var n=t.webkitMatchesSelector||t.mozMatchesSelector||t.oMatchesSelector||t.matchesSelector;if(n){return n.call(t,e)}var i,r=t.parentNode,o=!r;return o&&(r=O).appendChild(t),i=~T.qsa(r,e).indexOf(t),o&&O.removeChild(t),i},C=function(t){return t.replace(/-+(.)?/g,function(t,e){return e?e.toUpperCase():""})},N=function(t){return s.call(t,function(e,n){return t.indexOf(e)==n})},T.fragment=function(e,i,r){var s,u,f;return h.test(e)&&(s=n(a.createElement(RegExp.$1))),s||(e.replace&&(e=e.replace(p,"<$1></$2>")),i===t&&(i=l.test(e)&&RegExp.$1),i in b||(i="*"),f=b[i],f.innerHTML=""+e,s=n.each(o.call(f.childNodes),function(){f.removeChild(this)})),M(r)&&(u=n(s),n.each(r,function(t,e){g.indexOf(t)>-1?u[t](e):u.attr(t,e)})),s},T.Z=function(t,e){return t=t||[],t.__proto__=n.fn,t.selector=e||"",t},T.isZ=function(t){return t instanceof T.Z},T.init=function(e,i){var r;if(!e){return T.Z()}if("string"==typeof e){if(e=e.trim(),"<"==e[0]&&l.test(e)){r=T.fragment(e,RegExp.$1,i),e=null}else{if(i!==t){return n(i).find(e)}r=T.qsa(a,e)}}else{if(Z(e)){return n(a).ready(e)}if(T.isZ(e)){return e}if(A(e)){r=k(e)}else{if(D(e)){r=[e],e=null}else{if(l.test(e)){r=T.fragment(e.trim(),RegExp.$1,i),e=null}else{if(i!==t){return n(i).find(e)}r=T.qsa(a,e)}}}}return T.Z(r,e)},n=function(t,e){return T.init(t,e)},n.extend=function(t){var e,n=o.call(arguments,1);return"boolean"==typeof t&&(e=t,t=n.shift()),n.forEach(function(n){B(t,n,e)}),t},T.qsa=function(t,e){var n,i="#"==e[0],r=!i&&"."==e[0],s=i||r?e.slice(1):e,a=E.test(s);return $(t)&&a&&i?(n=t.getElementById(s))?[n]:[]:1!==t.nodeType&&9!==t.nodeType?[]:o.call(a&&!i?r?t.getElementsByClassName(s):t.getElementsByTagName(e):t.querySelectorAll(e))},n.contains=a.documentElement.contains?function(t,e){return t!==e&&t.contains(e)}:function(t,e){for(;e&&(e=e.parentNode);){if(e===t){return !0}}return !1},n.type=L,n.isFunction=Z,n.isWindow=_,n.isArray=A,n.isPlainObject=M,n.isEmptyObject=function(t){var e;for(e in t){return !1}return !0},n.inArray=function(t,e,n){return r.indexOf.call(e,t,n)},n.camelCase=C,n.trim=function(t){return null==t?"":String.prototype.trim.call(t)},n.uuid=0,n.support={},n.expr={},n.map=function(t,e){var n,r,o,i=[];if(R(t)){for(r=0;r<t.length;r++){n=e(t[r],r),null!=n&&i.push(n)}}else{for(o in t){n=e(t[o],o),null!=n&&i.push(n)}}return z(i)},n.each=function(t,e){var n,i;if(R(t)){for(n=0;n<t.length;n++){if(e.call(t[n],n,t[n])===!1){return t}}}else{for(i in t){if(e.call(t[i],i,t[i])===!1){return t}}}return t},n.grep=function(t,e){return s.call(t,e)},window.JSON&&(n.parseJSON=JSON.parse),n.each("Boolean Number String Function Array Date RegExp Object Error".split(" "),function(t,e){j["[object "+e+"]"]=e.toLowerCase()}),n.fn={forEach:r.forEach,reduce:r.reduce,push:r.push,sort:r.sort,indexOf:r.indexOf,concat:r.concat,map:function(t){return n(n.map(this,function(e,n){return t.call(e,n,e)}))},slice:function(){return n(o.apply(this,arguments))},ready:function(t){return w.test(a.readyState)&&a.body?t(n):a.addEventListener("DOMContentLoaded",function(){t(n)},!1),this},get:function(e){return e===t?o.call(this):this[e>=0?e:e+this.length]},toArray:function(){return this.get()},size:function(){return this.length},remove:function(){return this.each(function(){null!=this.parentNode&&this.parentNode.removeChild(this)})},each:function(t){return r.every.call(this,function(e,n){return t.call(e,n,e)!==!1}),this},filter:function(t){return Z(t)?this.not(this.not(t)):n(s.call(this,function(e){return T.matches(e,t)}))},add:function(t,e){return n(N(this.concat(n(t,e))))},is:function(t){return this.length>0&&T.matches(this[0],t)},not:function(e){var i=[];if(Z(e)&&e.call!==t){this.each(function(t){e.call(this,t)||i.push(this)})}else{var r="string"==typeof e?this.filter(e):R(e)&&Z(e.item)?o.call(e):n(e);this.forEach(function(t){r.indexOf(t)<0&&i.push(t)})}return n(i)},has:function(t){return this.filter(function(){return D(t)?n.contains(this,t):n(this).find(t).size()})},eq:function(t){return -1===t?this.slice(t):this.slice(t,+t+1)},first:function(){var t=this[0];return t&&!D(t)?t:n(t)},last:function(){var t=this[this.length-1];return t&&!D(t)?t:n(t)},find:function(t){var e,i=this;return e=t?"object"==typeof t?n(t).filter(function(){var t=this;return r.some.call(i,function(e){return n.contains(e,t)})}):1==this.length?n(T.qsa(this[0],t)):this.map(function(){return T.qsa(this,t)}):n()},closest:function(t,e){var i=this[0],r=!1;for("object"==typeof t&&(r=n(t));i&&!(r?r.indexOf(i)>=0:T.matches(i,t));){i=i!==e&&!$(i)&&i.parentNode}return n(i)},parents:function(t){for(var e=[],i=this;i.length>0;){i=n.map(i,function(t){return(t=t.parentNode)&&!$(t)&&e.indexOf(t)<0?(e.push(t),t):void 0})}return U(e,t)},parent:function(t){return U(N(this.pluck("parentNode")),t)},children:function(t){return U(this.map(function(){return V(this)}),t)},contents:function(){return this.map(function(){return o.call(this.childNodes)})},siblings:function(t){return U(this.map(function(t,e){return s.call(V(e.parentNode),function(t){return t!==e})}),t)},empty:function(){return this.each(function(){this.innerHTML=""})},pluck:function(t){return n.map(this,function(e){return e[t]})},show:function(){return this.each(function(){"none"==this.style.display&&(this.style.display=""),"none"==getComputedStyle(this,"").getPropertyValue("display")&&(this.style.display=I(this.nodeName))})},replaceWith:function(t){return this.before(t).remove()},wrap:function(t){var e=Z(t);if(this[0]&&!e){var i=n(t).get(0),r=i.parentNode||this.length>1}return this.each(function(o){n(this).wrapAll(e?t.call(this,o):r?i.cloneNode(!0):i)})},wrapAll:function(t){if(this[0]){n(this[0]).before(t=n(t));for(var e;(e=t.children()).length;){t=e.first()}n(t).append(this)}return this},wrapInner:function(t){var e=Z(t);return this.each(function(i){var r=n(this),o=r.contents(),s=e?t.call(this,i):t;o.length?o.wrapAll(s):r.append(s)})},unwrap:function(){return this.parent().each(function(){n(this).replaceWith(n(this).children())}),this},clone:function(){return this.map(function(){return this.cloneNode(!0)})},hide:function(){return this.css("display","none")},toggle:function(e){return this.each(function(){var i=n(this);(e===t?"none"==i.css("display"):e)?i.show():i.hide()})},prev:function(t){return n(this.pluck("previousElementSibling")).filter(t||"*")},next:function(t){return n(this.pluck("nextElementSibling")).filter(t||"*")},html:function(t){return 0 in arguments?this.each(function(e){var i=this.innerHTML;n(this).empty().append(J(this,t,e,i))}):0 in this?this[0].innerHTML:null},text:function(t){return 0 in arguments?this.each(function(e){var n=J(this,t,e,this.textContent);this.textContent=null==n?"":""+n}):0 in this?this[0].textContent:null},attr:function(n,i){var r;return"string"!=typeof n||1 in arguments?this.each(function(t){if(1===this.nodeType){if(D(n)){for(e in n){X(this,e,n[e])}}else{X(this,n,J(this,i,t,this.getAttribute(n)))}}}):this.length&&1===this[0].nodeType?!(r=this[0].getAttribute(n))&&n in this[0]?this[0][n]:r:t},removeAttr:function(t){return this.each(function(){1===this.nodeType&&t.split(" ").forEach(function(t){X(this,t)},this)})},prop:function(t,e){return t=P[t]||t,1 in arguments?this.each(function(n){this[t]=J(this,e,n,this[t])}):this[0]&&this[0][t]},data:function(e,n){var i="data-"+e.replace(m,"-$1").toLowerCase(),r=1 in arguments?this.attr(i,n):this.attr(i);return null!==r?Y(r):t},val:function(t){return 0 in arguments?this.each(function(e){this.value=J(this,t,e,this.value)}):this[0]&&(this[0].multiple?n(this[0]).find("option").filter(function(){return this.selected}).pluck("value"):this[0].value)},offset:function(t){if(t){return this.each(function(e){var i=n(this),r=J(this,t,e,i.offset()),o=i.offsetParent().offset(),s={top:r.top-o.top,left:r.left-o.left};"static"==i.css("position")&&(s.position="relative"),i.css(s)})}if(!this.length){return null}var e=this[0].getBoundingClientRect();return{left:e.left+window.pageXOffset,top:e.top+window.pageYOffset,width:Math.round(e.width),height:Math.round(e.height)}},css:function(t,i){if(arguments.length<2){var r,o=this[0];if(!o){return}if(r=getComputedStyle(o,""),"string"==typeof t){return o.style[C(t)]||r.getPropertyValue(t)}if(A(t)){var s={};return n.each(t,function(t,e){s[e]=o.style[C(e)]||r.getPropertyValue(e)}),s}}var a="";if("string"==L(t)){i||0===i?a=F(t)+":"+H(t,i):this.each(function(){this.style.removeProperty(F(t))})}else{for(e in t){t[e]||0===t[e]?a+=F(e)+":"+H(e,t[e])+";":this.each(function(){this.style.removeProperty(F(e))})}}return this.each(function(){this.style.cssText+=";"+a})},index:function(t){return t?this.indexOf(n(t)[0]):this.parent().children().indexOf(this[0])},hasClass:function(t){return t?r.some.call(this,function(t){return this.test(W(t))},q(t)):!1},addClass:function(t){return t?this.each(function(e){if("className" in this){i=[];var r=W(this),o=J(this,t,e,r);o.split(/\s+/g).forEach(function(t){n(this).hasClass(t)||i.push(t)},this),i.length&&W(this,r+(r?" ":"")+i.join(" "))}}):this},removeClass:function(e){return this.each(function(n){if("className" in this){if(e===t){return W(this,"")}i=W(this),J(this,e,n,i).split(/\s+/g).forEach(function(t){i=i.replace(q(t)," ")}),W(this,i.trim())}})},toggleClass:function(e,i){return e?this.each(function(r){var o=n(this),s=J(this,e,r,W(this));s.split(/\s+/g).forEach(function(e){(i===t?!o.hasClass(e):i)?o.addClass(e):o.removeClass(e)})}):this},scrollTop:function(e){if(this.length){var n="scrollTop" in this[0];return e===t?n?this[0].scrollTop:this[0].pageYOffset:this.each(n?function(){this.scrollTop=e}:function(){this.scrollTo(this.scrollX,e)})}},scrollLeft:function(e){if(this.length){var n="scrollLeft" in this[0];return e===t?n?this[0].scrollLeft:this[0].pageXOffset:this.each(n?function(){this.scrollLeft=e}:function(){this.scrollTo(e,this.scrollY)})}},position:function(){if(this.length){var t=this[0],e=this.offsetParent(),i=this.offset(),r=d.test(e[0].nodeName)?{top:0,left:0}:e.offset();return i.top-=parseFloat(n(t).css("margin-top"))||0,i.left-=parseFloat(n(t).css("margin-left"))||0,r.top+=parseFloat(n(e[0]).css("border-top-width"))||0,r.left+=parseFloat(n(e[0]).css("border-left-width"))||0,{top:i.top-r.top,left:i.left-r.left}}},offsetParent:function(){return this.map(function(){for(var t=this.offsetParent||a.body;t&&!d.test(t.nodeName)&&"static"==n(t).css("position");){t=t.offsetParent}return t})}},n.fn.detach=n.fn.remove,["width","height"].forEach(function(e){var i=e.replace(/./,function(t){return t[0].toUpperCase()});n.fn[e]=function(r){var o,s=this[0];return r===t?_(s)?s["inner"+i]:$(s)?s.documentElement["scroll"+i]:(o=this.offset())&&o[e]:this.each(function(t){s=n(this),s.css(e,J(this,r,t,s[e]()))})}}),v.forEach(function(t,e){var i=e%2;n.fn[t]=function(){var t,o,r=n.map(arguments,function(e){return t=L(e),"object"==t||"array"==t||null==e?e:T.fragment(e)}),s=this.length>1;return r.length<1?this:this.each(function(t,u){o=i?u:u.parentNode,u=0==e?u.nextSibling:1==e?u.firstChild:2==e?u:null;var f=n.contains(a.documentElement,o);r.forEach(function(t){if(s){t=t.cloneNode(!0)}else{if(!o){return n(t).remove()}}o.insertBefore(t,u),f&&G(t,function(t){null==t.nodeName||"SCRIPT"!==t.nodeName.toUpperCase()||t.type&&"text/javascript"!==t.type||t.src||window.eval.call(window,t.innerHTML)})})})},n.fn[i?t+"To":"insert"+(e?"Before":"After")]=function(e){return n(e)[t](this),this}}),T.Z.prototype=n.fn,T.uniq=N,T.deserializeValue=Y,n.zepto=T,n}();window.Zepto=Zepto,void 0===window.$&&(window.$=Zepto),function(F){function M(a){return a._zid||(a._zid=T++)}function P(b,d,f,a){if(d=I(d),d.ns){var c=U(d.ns)}return(G[M(b)]||[]).filter(function(e){return !(!e||d.e&&e.e!=d.e||d.ns&&!c.test(e.ns)||f&&M(e.fn)!==M(f)||a&&e.sel!=a)})}function I(a){var b=(""+a).split(".");return{e:b[0],ns:b.slice(1).sort().join(" ")}}function U(a){return new RegExp("(?:^| )"+a.replace(" "," .* ?")+"(?: |$)")}function L(a,b){return a.del&&!C&&a.e in R||!!b}function Q(a){return V[a]||C&&R[a]||a}function B(m,g,b,c,p,s,l){var j=M(m),n=G[j]||(G[j]=[]);g.split(/\s/).forEach(function(d){if("ready"==d){return F(document).ready(b)}var e=I(d);e.fn=b,e.sel=p,e.e in V&&(b=function(f){var h=f.relatedTarget;return !h||h!==this&&!F.contains(this,h)?e.fn.apply(this,arguments):void 0}),e.del=s;var a=s||b;e.proxy=function(h){if(h=N(h),!h.isImmediatePropagationStopped()){h.data=c;var f=a.apply(m,h._args==K?[h]:[h].concat(h._args));return f===!1&&(h.preventDefault(),h.stopPropagation()),f}},e.i=n.length,n.push(e),"addEventListener" in m&&m.addEventListener(Q(e.e),e.proxy,L(e,l))})}function q(b,d,g,a,c){var f=M(b);(d||"").split(/\s/).forEach(function(h){P(b,h,g,a).forEach(function(i){delete G[f][i.i],"removeEventListener" in b&&b.removeEventListener(Q(i.e),i.proxy,L(i,c))})})}function N(b,a){return(a||!b.isDefaultPrevented)&&(a||(a=b),F.each(D,function(c,e){var d=a[c];b[c]=function(){return this[e]=z,d&&d.apply(a,arguments)},b[e]=W}),(a.defaultPrevented!==K?a.defaultPrevented:"returnValue" in a?a.returnValue===!1:a.getPreventDefault&&a.getPreventDefault())&&(b.isDefaultPrevented=z)),b}function k(b){var c,a={originalEvent:b};for(c in b){A.test(c)||b[c]===K||(a[c]=b[c])}return N(a,b)}var K,T=1,O=Array.prototype.slice,H=F.isFunction,J=function(a){return"string"==typeof a},G={},X={},C="onfocusin" in window,R={focus:"focusin",blur:"focusout"},V={mouseenter:"mouseover",mouseleave:"mouseout"};X.click=X.mousedown=X.mouseup=X.mousemove="MouseEvents",F.event={add:B,remove:q},F.proxy=function(d,f){var c=2 in arguments&&O.call(arguments,2);if(H(d)){var b=function(){return d.apply(f,c?c.concat(O.call(arguments)):arguments)};return b._zid=M(d),b}if(J(f)){return c?(c.unshift(d[f],d),F.proxy.apply(null,c)):F.proxy(d[f],d)}throw new TypeError("expected function")},F.fn.bind=function(a,b,c){return this.on(a,b,c)},F.fn.unbind=function(a,b){return this.off(a,b)},F.fn.one=function(b,c,d,a){return this.on(b,c,d,a,1)};var z=function(){return !0},W=function(){return !1},A=/^([A-Z]|returnValue$|layer[XY]$)/,D={preventDefault:"isDefaultPrevented",stopImmediatePropagation:"isImmediatePropagationStopped",stopPropagation:"isPropagationStopped"};F.fn.delegate=function(a,b,c){return this.on(b,a,c)},F.fn.undelegate=function(a,b,c){return this.off(b,a,c)},F.fn.live=function(a,b){return F(document.body).delegate(this.selector,a,b),this},F.fn.die=function(a,b){return F(document.body).undelegate(this.selector,a,b),this},F.fn.on=function(n,j,d,g,m){var o,b,i=this;return n&&!J(n)?(F.each(n,function(a,c){i.on(a,j,d,c,m)}),i):(J(j)||H(g)||g===!1||(g=d,d=j,j=K),(H(d)||d===!1)&&(g=d,d=K),g===!1&&(g=W),i.each(function(c,a){m&&(o=function(e){return q(a,e.type,g),g.apply(this,arguments)}),j&&(b=function(f){var l,h=F(f.target).closest(j,a).get(0);return h&&h!==a?(l=F.extend(k(f),{currentTarget:h,liveFired:a}),(o||g).apply(h,[l].concat(O.call(arguments,1)))):void 0}),B(a,n,g,d,j,b||o)}))},F.fn.off=function(f,c,d){var b=this;return f&&!J(f)?(F.each(f,function(a,g){b.off(a,c,g)}),b):(J(c)||H(d)||d===!1||(d=c,c=K),d===!1&&(d=W),b.each(function(){q(this,f,d,c)}))},F.fn.trigger=function(a,b){return a=J(a)||F.isPlainObject(a)?F.Event(a):N(a),a._args=b,this.each(function(){a.type in R&&"function"==typeof this[a.type]?this[a.type]():"dispatchEvent" in this?this.dispatchEvent(a):F(this).triggerHandler(a,b)})},F.fn.triggerHandler=function(c,d){var a,b;return this.each(function(f,e){a=k(J(c)?F.Event(c):c),a._args=d,a.target=e,F.each(P(e,c.type||c),function(g,h){return b=h.proxy(a),a.isImmediatePropagationStopped()?!1:void 0})}),b},"focusin focusout focus blur load resize scroll unload click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select keydown keypress keyup error".split(" ").forEach(function(a){F.fn[a]=function(b){return 0 in arguments?this.bind(a,b):this.trigger(a)}}),F.Event=function(b,d){J(b)||(d=b,b=d.type);var f=document.createEvent(X[b]||"Events"),a=!0;if(d){for(var c in d){"bubbles"==c?a=!!d[c]:f[c]=d[c]}}return f.initEvent(b,a,!0),N(f)}}(Zepto),function(t){function h(e,n,i){var r=t.Event(n);return t(e).trigger(r,i),!r.isDefaultPrevented()}function p(t,e,i,r){return t.global?h(e||n,i,r):void 0}function d(e){e.global&&0===t.active++&&p(e,null,"ajaxStart")}function m(e){e.global&&!--t.active&&p(e,null,"ajaxStop")}function g(t,e){var n=e.context;return e.beforeSend.call(n,t,e)===!1||p(e,n,"ajaxBeforeSend",[t,e])===!1?!1:void p(e,n,"ajaxSend",[t,e])}function v(t,e,n,i){var r=n.context,o="success";n.success.call(r,t,o,e),i&&i.resolveWith(r,[t,o,e]),p(n,r,"ajaxSuccess",[e,n,t]),x(o,e,n)}function y(t,e,n,i,r){var o=i.context;i.error.call(o,n,e,t),r&&r.rejectWith(o,[n,e,t]),p(i,o,"ajaxError",[n,i,t||e]),x(e,n,i)}function x(t,e,n){var i=n.context;n.complete.call(i,e,t),p(n,i,"ajaxComplete",[e,n]),m(n)}function b(){}function w(t){return t&&(t=t.split(";",2)[0]),t&&(t==f?"html":t==u?"json":s.test(t)?"script":a.test(t)&&"xml")||"text"}function E(t,e){return""==e?t:(t+"&"+e).replace(/[&?]{1,2}/,"?")}function j(e){e.processData&&e.data&&"string"!=t.type(e.data)&&(e.data=t.param(e.data,e.traditional)),!e.data||e.type&&"GET"!=e.type.toUpperCase()||(e.url=E(e.url,e.data),e.data=void 0)}function S(e,n,i,r){return t.isFunction(n)&&(r=i,i=n,n=void 0),t.isFunction(i)||(r=i,i=void 0),{url:e,data:n,success:i,dataType:r}}function C(e,n,i,r){var o,s=t.isArray(n),a=t.isPlainObject(n);t.each(n,function(n,u){o=t.type(u),r&&(n=i?r:r+"["+(a||"object"==o||"array"==o?n:"")+"]"),!r&&s?e.add(u.name,u.value):"array"==o||!i&&"object"==o?C(e,u,i,n):e.add(n,u)})}var i,r,e=0,n=window.document,o=/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,s=/^(?:text|application)\/javascript/i,a=/^(?:text|application)\/xml/i,u="application/json",f="text/html",c=/^\s*$/,l=n.createElement("a");l.href=window.location.href,t.active=0,t.ajaxJSONP=function(i,r){if(!("type" in i)){return t.ajax(i)}var f,h,o=i.jsonpCallback,s=(t.isFunction(o)?o():o)||"jsonp"+ ++e,a=n.createElement("script"),u=window[s],c=function(e){t(a).triggerHandler("error",e||"abort")},l={abort:c};return r&&r.promise(l),t(a).on("load error",function(e,n){clearTimeout(h),t(a).off().remove(),"error"!=e.type&&f?v(f[0],l,i,r):y(null,n||"error",l,i,r),window[s]=u,f&&t.isFunction(u)&&u(f[0]),u=f=void 0}),g(l,i)===!1?(c("abort"),l):(window[s]=function(){f=arguments},a.src=i.url.replace(/\?(.+)=\?/,"?$1="+s),n.head.appendChild(a),i.timeout>0&&(h=setTimeout(function(){c("timeout")},i.timeout)),l)},t.ajaxSettings={type:"GET",beforeSend:b,success:b,error:b,complete:b,context:null,global:!0,xhr:function(){return new window.XMLHttpRequest},accepts:{script:"text/javascript, application/javascript, application/x-javascript",json:u,xml:"application/xml, text/xml",html:f,text:"text/plain"},crossDomain:!1,timeout:0,processData:!0,cache:!0},t.ajax=function(e){var a,o=t.extend({},e||{}),s=t.Deferred&&t.Deferred();for(i in t.ajaxSettings){void 0===o[i]&&(o[i]=t.ajaxSettings[i])}d(o),o.crossDomain||(a=n.createElement("a"),a.href=o.url,a.href=a.href,o.crossDomain=l.protocol+"//"+l.host!=a.protocol+"//"+a.host),o.url||(o.url=window.location.toString()),j(o);var u=o.dataType,f=/\?.+=\?/.test(o.url);if(f&&(u="jsonp"),o.cache!==!1&&(e&&e.cache===!0||"script"!=u&&"jsonp"!=u)||(o.url=E(o.url,"_="+Date.now())),"jsonp"==u){return f||(o.url=E(o.url,o.jsonp?o.jsonp+"=?":o.jsonp===!1?"":"callback=?")),t.ajaxJSONP(o,s)}var C,h=o.accepts[u],p={},m=function(t,e){p[t.toLowerCase()]=[t,e]},x=/^([\w-]+:)\/\//.test(o.url)?RegExp.$1:window.location.protocol,S=o.xhr(),T=S.setRequestHeader;if(s&&s.promise(S),o.crossDomain||m("X-Requested-With","XMLHttpRequest"),m("Accept",h||"*/*"),(h=o.mimeType||h)&&(h.indexOf(",")>-1&&(h=h.split(",",2)[0]),S.overrideMimeType&&S.overrideMimeType(h)),(o.contentType||o.contentType!==!1&&o.data&&"GET"!=o.type.toUpperCase())&&m("Content-Type",o.contentType||"application/x-www-form-urlencoded"),o.headers){for(r in o.headers){m(r,o.headers[r])}}if(S.setRequestHeader=m,S.onreadystatechange=function(){if(4==S.readyState){S.onreadystatechange=b,clearTimeout(C);var e,n=!1;if(S.status>=200&&S.status<300||304==S.status||0==S.status&&"file:"==x){u=u||w(o.mimeType||S.getResponseHeader("content-type")),e=S.responseText;try{"script"==u?(1,eval)(e):"xml"==u?e=S.responseXML:"json"==u&&(e=c.test(e)?null:t.parseJSON(e))}catch(i){n=i}n?y(n,"parsererror",S,o,s):v(e,S,o,s)}else{y(S.statusText||null,S.status?"error":"abort",S,o,s)}}},g(S,o)===!1){return S.abort(),y(null,"abort",S,o,s),S}if(o.xhrFields){for(r in o.xhrFields){S[r]=o.xhrFields[r]}}var N="async" in o?o.async:!0;S.open(o.type,o.url,N,o.username,o.password);for(r in p){T.apply(S,p[r])}return o.timeout>0&&(C=setTimeout(function(){S.onreadystatechange=b,S.abort(),y(null,"timeout",S,o,s)},o.timeout)),S.send(o.data?o.data:null),S},t.get=function(){return t.ajax(S.apply(null,arguments))},t.post=function(){var e=S.apply(null,arguments);return e.type="POST",t.ajax(e)},t.getJSON=function(){var e=S.apply(null,arguments);return e.dataType="json",t.ajax(e)},t.fn.load=function(e,n,i){if(!this.length){return this}var a,r=this,s=e.split(/\s/),u=S(e,n,i),f=u.success;return s.length>1&&(u.url=s[0],a=s[1]),u.success=function(e){r.html(a?t("<div>").html(e.replace(o,"")).find(a):e),f&&f.apply(r,arguments)},t.ajax(u),this};var T=encodeURIComponent;t.param=function(e,n){var i=[];return i.add=function(e,n){t.isFunction(n)&&(n=n()),null==n&&(n=""),this.push(T(e)+"="+T(n))},C(i,e,n),i.join("&").replace(/%20/g,"+")}}(Zepto),function(a){a.fn.serializeArray=function(){var d,f,b=[],c=function(e){return e.forEach?e.forEach(c):void b.push({name:d,value:e})};return this[0]&&a.each(this[0].elements,function(e,g){f=g.type,d=g.name,d&&"fieldset"!=g.nodeName.toLowerCase()&&!g.disabled&&"submit"!=f&&"reset"!=f&&"button"!=f&&"file"!=f&&("radio"!=f&&"checkbox"!=f||g.checked)&&c(a(g).val())}),b},a.fn.serialize=function(){var b=[];return this.serializeArray().forEach(function(c){b.push(encodeURIComponent(c.name)+"="+encodeURIComponent(c.value))}),b.join("&")},a.fn.submit=function(b){if(0 in arguments){this.bind("submit",b)}else{if(this.length){var c=a.Event("submit");this.eq(0).trigger(c),c.isDefaultPrevented()||this.get(0).submit()}}return this}}(Zepto),function(a){"__proto__" in {}||a.extend(a.zepto,{Z:function(d,f){return d=d||[],a.extend(d,a.fn),d.selector=f||"",d.__Z=!0,d},isZ:function(d){return"array"===a.type(d)&&"__Z" in d}});try{getComputedStyle(void 0)}catch(b){var c=getComputedStyle;window.getComputedStyle=function(d){try{return c(d)}catch(f){return null}}}}(Zepto);(function(d,f){var n="",s,m={Webkit:"webkit",Moz:"",O:"o"},a=document.createElement("div"),l=/^((translate|rotate|scale)(X|Y|Z|3d)?|matrix(3d)?|perspective|skew(X|Y)?)$/i,j,o,i,k,e,h,r,p,b,q={};function c(t){return t.replace(/([a-z])([A-Z])/,"$1-$2").toLowerCase()}function g(t){return s?s+t:t.toLowerCase()}d.each(m,function(u,t){if(a.style[u+"TransitionProperty"]!==f){n="-"+u.toLowerCase()+"-";s=t;return false}});j=n+"transform";q[o=n+"transition-property"]=q[i=n+"transition-duration"]=q[e=n+"transition-delay"]=q[k=n+"transition-timing-function"]=q[h=n+"animation-name"]=q[r=n+"animation-duration"]=q[b=n+"animation-delay"]=q[p=n+"animation-timing-function"]="";d.fx={off:(s===f&&a.style.transitionProperty===f),speeds:{_default:400,fast:200,slow:600},cssPrefix:n,transitionEnd:g("TransitionEnd"),animationEnd:g("AnimationEnd")};d.fn.animate=function(u,v,w,x,t){if(d.isFunction(v)){x=v,w=f,v=f}if(d.isFunction(w)){x=w,w=f}if(d.isPlainObject(v)){w=v.easing,x=v.complete,t=v.delay,v=v.duration}if(v){v=(typeof v=="number"?v:(d.fx.speeds[v]||d.fx.speeds._default))/1000}if(t){t=parseFloat(t)/1000}return this.anim(u,v,w,x,t)};d.fn.anim=function(B,w,v,D,x){var C,z={},F,A="",y=this,u,E=d.fx.transitionEnd,t=false;if(w===f){w=d.fx.speeds._default/1000}if(x===f){x=0}if(d.fx.off){w=0}if(typeof B=="string"){z[h]=B;z[r]=w+"s";z[b]=x+"s";z[p]=(v||"linear");E=d.fx.animationEnd}else{F=[];for(C in B){if(l.test(C)){A+=C+"("+B[C]+") "}else{z[C]=B[C],F.push(c(C))}}if(A){z[j]=A,F.push(j)}if(w>0&&typeof B==="object"){z[o]=F.join(", ");z[i]=w+"s";z[e]=x+"s";z[k]=(v||"linear")}}u=function(G){if(typeof G!=="undefined"){if(G.target!==G.currentTarget){return}d(G.target).unbind(E,u)}else{d(this).unbind(E,u)}t=true;d(this).css(q);D&&D.call(this)};if(w>0){this.bind(E,u);setTimeout(function(){if(t){return}u.call(y)},((w+x)*1000)+25)}this.size()&&this.get(0).clientLeft;this.css(z);if(w<=0){setTimeout(function(){y.each(function(){u.call(this)})},0)}return this};a=null})(Zepto);var org=(function(){document.body.addEventListener("touchstart",function(){});var a={_ajax:function(b){$.ajax({url:b.url,type:b.type,data:b.data,dataType:b.dataType,async:b.async=="undefined"?true:false,beforeSend:function(d,c){b.beforeSend&&b.beforeSend(d);if(!a._csrfSafeMethod(c.type)&&a._sameOrigin(c.url)){d.setRequestHeader("X-CSRFToken",a._getCookie("csrftoken"))}},success:function(c){b.success&&b.success(c)},error:function(c){b.error&&b.error(c)},complete:function(){b.complete&&b.complete()}})},_getQueryStringByName:function(c){var b=location.search.match(new RegExp("[?&]"+c+"=([^&]+)","i"));if(b==null||b.length<1){return""}return b[1]},_getCookie:function(b){var d,f,e,c;f=null;if(document.cookie&&document.cookie!==""){e=document.cookie.split(";");c=0;while(c<e.length){d=$.trim(e[c]);if(d.substring(0,b.length+1)===(b+"=")){f=decodeURIComponent(d.substring(b.length+1));break}c++}}return f},_csrfSafeMethod:function(b){return/^(GET|HEAD|OPTIONS|TRACE)$/.test(b)},_sameOrigin:function(c){var e,b,f,d;e=document.location.host;f=document.location.protocol;d="//"+e;b=f+d;return(c===b||c.slice(0,b.length+1)===b+"/")||(c===d||c.slice(0,d.length+1)===d+"/")||!(/^(\/\/|http:|https:).*/.test(c))},_setShareData:function(d,f,c){var b={};if(typeof d=="object"){for(var e in d){b[e]=d[e]}}typeof f=="function"&&f!="undefined"?b.success=f:"";typeof c=="function"&&c!="undefined"?b.cancel=c:"";return b},_onMenuShareAppMessage:function(c,d,b){wx.onMenuShareAppMessage(a._setShareData(c,d,b))},_onMenuShareTimeline:function(c,d,b){wx.onMenuShareTimeline(a._setShareData(c,d,b))},_onMenuShareQQ:function(){wx.onMenuShareQQ(a._setShareData(ops,suFn,canFn))}};return{ajax:a._ajax,getQueryStringByName:a._getQueryStringByName,getCookie:a._getCookie,onMenuShareAppMessage:a._onMenuShareAppMessage,onMenuShareTimeline:a._onMenuShareTimeline,onMenuShareQQ:a._onMenuShareQQ,}})();(function(){var a=["scanQRCode","onMenuShareAppMessage","onMenuShareTimeline","onMenuShareQQ",];org.ajax({type:"GET",url:"/weixin/api/jsapi_config/",dataType:"json",success:function(b){wx.config({debug:false,appId:b.appId,timestamp:b.timestamp,nonceStr:b.nonceStr,signature:b.signature,jsApiList:a})}});wx.ready(function(){var f="https://www.wanglibao.com",b="遇到十年前的自己",e=f+"/static/imgs/mobile_activity/app_ten_year/weixin_img_300.jpg",c=f+"/activity/app_ten_year/",d="遇到十年前的自己",g="我刚遇到十年前的自己，你也来试试吧...";org.onMenuShareAppMessage({title:d,desc:g,link:c,imgUrl:e});org.onMenuShareTimeline({title:"我刚遇到十年前的自己，你也来试试吧...",link:c,imgUrl:e});org.onMenuShareQQ({title:d,desc:g,link:c,imgUrl:e})})})();

