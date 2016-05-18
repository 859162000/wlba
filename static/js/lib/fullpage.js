/**
 * fullPage 2.5.4
 * https://github.com/alvarotrigo/fullPage.js
 * MIT licensed
 *
 * Copyright (C) 2013 alvarotrigo.com - A project by Alvaro Trigo
 */
(function(b){b.fn.fullpage=function(c){function pa(a){a.find(".fp-slides").after('<div class="fp-controlArrow fp-prev"></div><div class="fp-controlArrow fp-next"></div>');"#fff"!=c.controlArrowColor&&(a.find(".fp-controlArrow.fp-next").css("border-color","transparent transparent transparent "+c.controlArrowColor),a.find(".fp-controlArrow.fp-prev").css("border-color","transparent "+c.controlArrowColor+" transparent transparent"));c.loopHorizontal||a.find(".fp-controlArrow.fp-prev").hide()}function qa(){b("body").append('<div id="fp-nav"><ul></ul></div>');
k=b("#fp-nav");k.css("color",c.navigationColor);k.addClass(c.navigationPosition);for(var a=0;a<b(".fp-section").length;a++){var d="";c.anchors.length&&(d=c.anchors[a]);var d='<li><a href="#'+d+'"><span></span></a>',e=c.navigationTooltips[a];void 0!=e&&""!=e&&(d+='<div class="fp-tooltip '+c.navigationPosition+'">'+e+"</div>");d+="</li>";k.find("ul").append(d)}}function R(){b(".fp-section").each(function(){var a=b(this).find(".fp-slide");a.length?a.each(function(){y(b(this))}):y(b(this))});b.isFunction(c.afterRender)&&
c.afterRender.call(this)}function S(){if(!c.autoScrolling||c.scrollBar){var a=b(window).scrollTop(),d=0,e=Math.abs(a-b(".fp-section").first().offset().top);b(".fp-section").each(function(c){var f=Math.abs(a-b(this).offset().top);f<e&&(d=c,e=f)});var f=b(".fp-section").eq(d)}if(!c.autoScrolling&&!f.hasClass("active")){F=!0;var ra=b(".fp-section.active").index(".fp-section")+1,g=G(f),h=f.data("anchor"),k=f.index(".fp-section")+1,l=f.find(".fp-slide.active");if(l.length)var n=l.data("anchor"),t=l.index();
f.addClass("active").siblings().removeClass("active");m||(b.isFunction(c.onLeave)&&c.onLeave.call(this,ra,k,g),b.isFunction(c.afterLoad)&&c.afterLoad.call(this,h,k));H(h,0);c.anchors.length&&!m&&(p=h,I(t,n,h,k));clearTimeout(T);T=setTimeout(function(){F=!1},100)}c.scrollBar&&(clearTimeout(U),U=setTimeout(function(){m||q(f)},1E3))}function V(a){return scrollable=a.find(".fp-slides").length?a.find(".fp-slide.active").find(".fp-scrollable"):a.find(".fp-scrollable")}function z(a,d){if(l[a]){if("down"==
a)var c="bottom",f=b.fn.fullpage.moveSectionDown;else c="top",f=b.fn.fullpage.moveSectionUp;if(0<d.length)if(c="top"===c?!d.scrollTop():"bottom"===c?d.scrollTop()+1+d.innerHeight()>=d[0].scrollHeight:void 0,c)f();else return!0;else f()}}function sa(a){var d=a.originalEvent;if(!W(a.target)){c.autoScrolling&&!c.scrollBar&&a.preventDefault();a=b(".fp-section.active");var e=V(a);m||t||(d=X(d),u=d.y,A=d.x,a.find(".fp-slides").length&&Math.abs(B-A)>Math.abs(v-u)?Math.abs(B-A)>b(window).width()/100*c.touchSensitivity&&
(B>A?l.right&&b.fn.fullpage.moveSlideRight():l.left&&b.fn.fullpage.moveSlideLeft()):c.autoScrolling&&!c.scrollBar&&Math.abs(v-u)>b(window).height()/100*c.touchSensitivity&&(v>u?z("down",e):u>v&&z("up",e)))}}function W(a,d){d=d||0;var e=b(a).parent();return d<c.normalScrollElementTouchThreshold&&e.is(c.normalScrollElements)?!0:d==c.normalScrollElementTouchThreshold?!1:W(e,++d)}function ta(a){a=X(a.originalEvent);v=a.y;B=a.x}function r(a){if(c.autoScrolling){a=window.event||a;var d=Math.max(-1,Math.min(1,
a.wheelDelta||-a.deltaY||-a.detail));c.scrollBar&&(a.preventDefault?a.preventDefault():a.returnValue=!1);a=b(".fp-section.active");a=V(a);m||(0>d?z("down",a):z("up",a));return!1}}function Y(a){var d=b(".fp-section.active").find(".fp-slides");if(d.length&&!t){var e=d.find(".fp-slide.active"),f=null,f="prev"===a?e.prev(".fp-slide"):e.next(".fp-slide");if(!f.length){if(!c.loopHorizontal)return;f="prev"===a?e.siblings(":last"):e.siblings(":first")}t=!0;w(d,f)}}function Z(){b(".fp-slide.active").each(function(){J(b(this))})}
function q(a,d,e){var f=a.position();if("undefined"!==typeof f&&(d={element:a,callback:d,isMovementUp:e,dest:f,dtop:f.top,yMovement:G(a),anchorLink:a.data("anchor"),sectionIndex:a.index(".fp-section"),activeSlide:a.find(".fp-slide.active"),activeSection:b(".fp-section.active"),leavingSection:b(".fp-section.active").index(".fp-section")+1,localIsResizing:x},!(d.activeSection.is(a)&&!x||c.scrollBar&&b(window).scrollTop()===d.dtop))){if(d.activeSlide.length)var g=d.activeSlide.data("anchor"),h=d.activeSlide.index();
c.autoScrolling&&c.continuousVertical&&"undefined"!==typeof d.isMovementUp&&(!d.isMovementUp&&"up"==d.yMovement||d.isMovementUp&&"down"==d.yMovement)&&(d.isMovementUp?b(".fp-section.active").before(d.activeSection.nextAll(".fp-section")):b(".fp-section.active").after(d.activeSection.prevAll(".fp-section").get().reverse()),n(b(".fp-section.active").position().top),Z(),d.wrapAroundElements=d.activeSection,d.dest=d.element.position(),d.dtop=d.dest.top,d.yMovement=G(d.element));a.addClass("active").siblings().removeClass("active");
m=!0;I(h,g,d.anchorLink,d.sectionIndex);b.isFunction(c.onLeave)&&!d.localIsResizing&&c.onLeave.call(this,d.leavingSection,d.sectionIndex+1,d.yMovement);ua(d);p=d.anchorLink;c.autoScrolling&&H(d.anchorLink,d.sectionIndex)}}function ua(a){if(c.css3&&c.autoScrolling&&!c.scrollBar)aa("translate3d(0px, -"+a.dtop+"px, 0px)",!0),setTimeout(function(){ba(a)},c.scrollingSpeed);else{var d=va(a);b(d.element).animate(d.options,c.scrollingSpeed,c.easing).promise().done(function(){ba(a)})}}function va(a){var b=
{};c.autoScrolling&&!c.scrollBar?(b.options={top:-a.dtop},b.element="."+ca):(b.options={scrollTop:a.dtop},b.element="html, body");return b}function wa(a){a.wrapAroundElements&&a.wrapAroundElements.length&&(a.isMovementUp?b(".fp-section:first").before(a.wrapAroundElements):b(".fp-section:last").after(a.wrapAroundElements),n(b(".fp-section.active").position().top),Z())}function ba(a){wa(a);b.isFunction(c.afterLoad)&&!a.localIsResizing&&c.afterLoad.call(this,a.anchorLink,a.sectionIndex+1);setTimeout(function(){m=
!1;b.isFunction(a.callback)&&a.callback.call(this)},600)}function da(){if(!F){var a=window.location.hash.replace("#","").split("/"),b=a[0],a=a[1];if(b.length){var c="undefined"===typeof p,f="undefined"===typeof p&&"undefined"===typeof a&&!t;(b&&b!==p&&!c||f||!t&&K!=a)&&L(b,a)}}}function w(a,d){var e=d.position(),f=a.find(".fp-slidesContainer").parent(),g=d.index(),h=a.closest(".fp-section"),k=h.index(".fp-section"),l=h.data("anchor"),n=h.find(".fp-slidesNav"),m=d.data("anchor"),q=x;if(c.onSlideLeave){var p=
h.find(".fp-slide.active").index(),r;r=p==g?"none":p>g?"left":"right";q||"none"===r||b.isFunction(c.onSlideLeave)&&c.onSlideLeave.call(this,l,k+1,p,r)}d.addClass("active").siblings().removeClass("active");"undefined"===typeof m&&(m=g);!c.loopHorizontal&&c.controlArrows&&(h.find(".fp-controlArrow.fp-prev").toggle(0!=g),h.find(".fp-controlArrow.fp-next").toggle(!d.is(":last-child")));h.hasClass("active")&&I(g,m,l,k);var u=function(){q||b.isFunction(c.afterSlideLoad)&&c.afterSlideLoad.call(this,l,k+
1,m,g);t=!1};c.css3?(e="translate3d(-"+e.left+"px, 0px, 0px)",ea(a.find(".fp-slidesContainer"),0<c.scrollingSpeed).css(fa(e)),setTimeout(function(){u()},c.scrollingSpeed,c.easing)):f.animate({scrollLeft:e.left},c.scrollingSpeed,c.easing,function(){u()});n.find(".active").removeClass("active");n.find("li").eq(g).find("a").addClass("active")}function ga(){ha();if(C){if("text"!==b(document.activeElement).attr("type")){var a=b(window).height();Math.abs(a-M)>20*Math.max(M,a)/100&&(b.fn.fullpage.reBuild(!0),
M=a)}}else clearTimeout(ia),ia=setTimeout(function(){b.fn.fullpage.reBuild(!0)},500)}function ha(){if(c.responsive){var a=g.hasClass("fp-responsive");b(window).width()<c.responsive?a||(b.fn.fullpage.setAutoScrolling(!1,"internal"),b("#fp-nav").hide(),g.addClass("fp-responsive")):a&&(b.fn.fullpage.setAutoScrolling(N.autoScrolling,"internal"),b("#fp-nav").show(),g.removeClass("fp-responsive"))}}function ea(a){var b="all "+c.scrollingSpeed+"ms "+c.easingcss3;a.removeClass("fp-notransition");return a.css({"-webkit-transition":b,
transition:b})}function O(a){return a.addClass("fp-notransition")}function xa(a,d){if(825>a||900>d){var c=Math.min(100*a/825,100*d/900).toFixed(2);b("body").css("font-size",c+"%")}else b("body").css("font-size","100%")}function H(a,d){c.menu&&(b(c.menu).find(".active").removeClass("active"),b(c.menu).find('[data-menuanchor="'+a+'"]').addClass("active"));c.navigation&&(b("#fp-nav").find(".active").removeClass("active"),a?b("#fp-nav").find('a[href="#'+a+'"]').addClass("active"):b("#fp-nav").find("li").eq(d).find("a").addClass("active"))}
function G(a){var d=b(".fp-section.active").index(".fp-section");a=a.index(".fp-section");return d==a?"none":d>a?"up":"down"}function y(a){a.css("overflow","hidden");var b=a.closest(".fp-section"),e=a.find(".fp-scrollable");if(e.length)var f=e.get(0).scrollHeight;else f=a.get(0).scrollHeight,c.verticalCentered&&(f=a.find(".fp-tableCell").get(0).scrollHeight);b=h-parseInt(b.css("padding-bottom"))-parseInt(b.css("padding-top"));f>b?e.length?e.css("height",b+"px").parent().css("height",b+"px"):(c.verticalCentered?
a.find(".fp-tableCell").wrapInner('<div class="fp-scrollable" />'):a.wrapInner('<div class="fp-scrollable" />'),a.find(".fp-scrollable").slimScroll({allowPageScroll:!0,height:b+"px",size:"10px",alwaysVisible:!0})):ja(a);a.css("overflow","")}function ja(a){a.find(".fp-scrollable").children().first().unwrap().unwrap();a.find(".slimScrollBar").remove();a.find(".slimScrollRail").remove()}function ka(a){a.addClass("fp-table").wrapInner('<div class="fp-tableCell" style="height:'+la(a)+'px;" />')}function la(a){var b=
h;if(c.paddingTop||c.paddingBottom)b=a,b.hasClass("fp-section")||(b=a.closest(".fp-section")),a=parseInt(b.css("padding-top"))+parseInt(b.css("padding-bottom")),b=h-a;return b}function aa(a,b){b?ea(g):O(g);g.css(fa(a));setTimeout(function(){g.removeClass("fp-notransition")},10)}function L(a,d){"undefined"===typeof d&&(d=0);var c=isNaN(a)?b('[data-anchor="'+a+'"]'):b(".fp-section").eq(a-1);a===p||c.hasClass("active")?ma(c,d):q(c,function(){ma(c,d)})}function ma(a,b){if("undefined"!=typeof b){var c=
a.find(".fp-slides"),f=c.find('[data-anchor="'+b+'"]');f.length||(f=c.find(".fp-slide").eq(b));f.length&&w(c,f)}}function ya(a,b){a.append('<div class="fp-slidesNav"><ul></ul></div>');var e=a.find(".fp-slidesNav");e.addClass(c.slidesNavPosition);for(var f=0;f<b;f++)e.find("ul").append('<li><a href="#"><span></span></a></li>');e.css("margin-left","-"+e.width()/2+"px");e.find("li").first().find("a").addClass("active")}function I(a,b,e,f){var g="";c.anchors.length?(a?("undefined"!==typeof e&&(g=e),"undefined"===
typeof b&&(b=a),K=b,na(g+"/"+b)):("undefined"!==typeof a&&(K=b),na(e)),D(location.hash)):"undefined"!==typeof a?D(f+"-"+a):D(String(f))}function na(a){if(c.recordHistory)location.hash=a;else if(C||P)history.replaceState(void 0,void 0,"#"+a);else{var b=window.location.href.split("#")[0];window.location.replace(b+"#"+a)}}function D(a){a=a.replace("/","-").replace("#","");b("body")[0].className=b("body")[0].className.replace(/\b\s?fp-viewing-[^\s]+\b/g,"");b("body").addClass("fp-viewing-"+a)}function za(){var a=
document.createElement("p"),b,c={webkitTransform:"-webkit-transform",OTransform:"-o-transform",msTransform:"-ms-transform",MozTransform:"-moz-transform",transform:"transform"};document.body.insertBefore(a,null);for(var f in c)void 0!==a.style[f]&&(a.style[f]="translate3d(1px,1px,1px)",b=window.getComputedStyle(a).getPropertyValue(c[f]));document.body.removeChild(a);return void 0!==b&&0<b.length&&"none"!==b}function oa(){return window.PointerEvent?{down:"pointerdown",move:"pointermove"}:{down:"MSPointerDown",
move:"MSPointerMove"}}function X(a){var b=[];b.y="undefined"!==typeof a.pageY&&(a.pageY||a.pageX)?a.pageY:a.touches[0].pageY;b.x="undefined"!==typeof a.pageX&&(a.pageY||a.pageX)?a.pageX:a.touches[0].pageX;return b}function J(a){b.fn.fullpage.setScrollingSpeed(0,"internal");w(a.closest(".fp-slides"),a);b.fn.fullpage.setScrollingSpeed(N.scrollingSpeed,"internal")}function n(a){c.scrollBar?g.scrollTop(a):c.css3?aa("translate3d(0px, -"+a+"px, 0px)",!1):g.css("top",-a)}function fa(a){return{"-webkit-transform":a,
"-moz-transform":a,"-ms-transform":a,transform:a}}function Aa(){n(0);b("#fp-nav, .fp-slidesNav, .fp-controlArrow").remove();b(".fp-section").css({height:"","background-color":"",padding:""});b(".fp-slide").css({width:""});g.css({height:"",position:"","-ms-touch-action":"","touch-action":""});b(".fp-section, .fp-slide").each(function(){ja(b(this));b(this).removeClass("fp-table active")});O(g);O(g.find(".fp-easing"));g.find(".fp-tableCell, .fp-slidesContainer, .fp-slides").each(function(){b(this).replaceWith(this.childNodes)});
b("html, body").scrollTop(0)}function Q(a,b,e){c[a]=b;"internal"!==e&&(N[a]=b)}function E(a,b){console&&console[a]&&console[a]("fullPage: "+b)}c=b.extend({menu:!1,anchors:[],navigation:!1,navigationPosition:"right",navigationColor:"#000",navigationTooltips:[],slidesNavigation:!1,slidesNavPosition:"bottom",scrollBar:!1,css3:!0,scrollingSpeed:700,autoScrolling:!0,easing:"easeInQuart",easingcss3:"ease",loopBottom:!1,loopTop:!1,loopHorizontal:!0,continuousVertical:!1,normalScrollElements:null,scrollOverflow:!1,
touchSensitivity:5,normalScrollElementTouchThreshold:5,keyboardScrolling:!0,animateAnchor:!0,recordHistory:!0,controlArrows:!0,controlArrowColor:"#fff",verticalCentered:!0,resize:!0,sectionsColor:[],paddingTop:0,paddingBottom:0,fixedElements:null,responsive:0,sectionSelector:".section",slideSelector:".slide",afterLoad:null,onLeave:null,afterRender:null,afterResize:null,afterReBuild:null,afterSlideLoad:null,onSlideLeave:null},c);(function(){c.continuousVertical&&(c.loopTop||c.loopBottom)&&(c.continuousVertical=
!1,E("warn","Option `loopTop/loopBottom` is mutually exclusive with `continuousVertical`; `continuousVertical` disabled"));c.continuousVertical&&c.scrollBar&&(c.continuousVertical=!1,E("warn","Option `scrollBar` is mutually exclusive with `continuousVertical`; `continuousVertical` disabled"));b.each(c.anchors,function(a,c){(b("#"+c).length||b('[name="'+c+'"]').length)&&E("error","data-anchor tags can not have the same value as any `id` element on the site (or `name` element for IE).")})})();b.extend(b.easing,
{easeInQuart:function(a,b,c,f,g){return f*(b/=g)*b*b*b+c}});b.fn.fullpage.setAutoScrolling=function(a,d){Q("autoScrolling",a,d);var e=b(".fp-section.active");c.autoScrolling&&!c.scrollBar?(b("html, body").css({overflow:"hidden",height:"100%"}),b.fn.fullpage.setRecordHistory(c.recordHistory,"internal"),g.css({"-ms-touch-action":"none","touch-action":"none"}),e.length&&n(e.position().top)):(b("html, body").css({overflow:"visible",height:"initial"}),b.fn.fullpage.setRecordHistory(!1,"internal"),g.css({"-ms-touch-action":"",
"touch-action":""}),n(0),b("html, body").scrollTop(e.position().top))};b.fn.fullpage.setRecordHistory=function(a,b){Q("recordHistory",a,b)};b.fn.fullpage.setScrollingSpeed=function(a,b){Q("scrollingSpeed",a,b)};b.fn.fullpage.setMouseWheelScrolling=function(a){a?document.addEventListener?(document.addEventListener("mousewheel",r,!1),document.addEventListener("wheel",r,!1)):document.attachEvent("onmousewheel",r):document.addEventListener?(document.removeEventListener("mousewheel",r,!1),document.removeEventListener("wheel",
r,!1)):document.detachEvent("onmousewheel",r)};b.fn.fullpage.setAllowScrolling=function(a,c){if("undefined"!=typeof c)c=c.replace(" ","").split(","),b.each(c,function(c,d){switch(d){case "up":l.up=a;break;case "down":l.down=a;break;case "left":l.left=a;break;case "right":l.right=a;break;case "all":b.fn.fullpage.setAllowScrolling(a)}});else if(a){if(b.fn.fullpage.setMouseWheelScrolling(!0),C||P)MSPointer=oa(),b(document).off("touchstart "+MSPointer.down).on("touchstart "+MSPointer.down,ta),b(document).off("touchmove "+
MSPointer.move).on("touchmove "+MSPointer.move,sa)}else if(b.fn.fullpage.setMouseWheelScrolling(!1),C||P)MSPointer=oa(),b(document).off("touchstart "+MSPointer.down),b(document).off("touchmove "+MSPointer.move)};b.fn.fullpage.setKeyboardScrolling=function(a){c.keyboardScrolling=a};b.fn.fullpage.moveSectionUp=function(){var a=b(".fp-section.active").prev(".fp-section");a.length||!c.loopTop&&!c.continuousVertical||(a=b(".fp-section").last());a.length&&q(a,null,!0)};b.fn.fullpage.moveSectionDown=function(){var a=
b(".fp-section.active").next(".fp-section");a.length||!c.loopBottom&&!c.continuousVertical||(a=b(".fp-section").first());a.length&&q(a,null,!1)};b.fn.fullpage.moveTo=function(a,c){var e="",e=isNaN(a)?b('[data-anchor="'+a+'"]'):b(".fp-section").eq(a-1);"undefined"!==typeof c?L(a,c):0<e.length&&q(e)};b.fn.fullpage.moveSlideRight=function(){Y("next")};b.fn.fullpage.moveSlideLeft=function(){Y("prev")};b.fn.fullpage.reBuild=function(a){x=!0;var d=b(window).width();h=b(window).height();c.resize&&xa(h,d);
b(".fp-section").each(function(){parseInt(b(this).css("padding-bottom"));parseInt(b(this).css("padding-top"));c.verticalCentered&&b(this).find(".fp-tableCell").css("height",la(b(this))+"px");b(this).css("height",h+"px");if(c.scrollOverflow){var a=b(this).find(".fp-slide");a.length?a.each(function(){y(b(this))}):y(b(this))}a=b(this).find(".fp-slides");a.length&&w(a,a.find(".fp-slide.active"))});b(".fp-section.active").position();d=b(".fp-section.active");d.index(".fp-section")&&q(d);x=!1;b.isFunction(c.afterResize)&&
a&&c.afterResize.call(this);b.isFunction(c.afterReBuild)&&!a&&c.afterReBuild.call(this)};var t=!1,C=navigator.userAgent.match(/(iPhone|iPod|iPad|Android|BlackBerry|BB10|Windows Phone|Tizen|Bada)/),P="ontouchstart"in window||0<navigator.msMaxTouchPoints||navigator.maxTouchPoints,g=b(this),h=b(window).height(),m=!1,x=!1,p,K,k,ca="fullpage-wrapper",l={up:!0,down:!0,left:!0,right:!0},N=jQuery.extend(!0,{},c);b.fn.fullpage.setAllowScrolling(!0);c.css3&&(c.css3=za());b(this).length?(g.css({height:"100%",
position:"relative"}),g.addClass(ca)):E("error","Error! Fullpage.js needs to be initialized with a selector. For example: $('#myContainer').fullpage();");b(c.sectionSelector).each(function(){b(this).addClass("fp-section")});b(c.slideSelector).each(function(){b(this).addClass("fp-slide")});c.navigation&&qa();b(".fp-section").each(function(a){var d=b(this),e=b(this).find(".fp-slide"),f=e.length;a||0!==b(".fp-section.active").length||b(this).addClass("active");b(this).css("height",h+"px");(c.paddingTop||
c.paddingBottom)&&b(this).css("padding",c.paddingTop+" 0 "+c.paddingBottom+" 0");"undefined"!==typeof c.sectionsColor[a]&&b(this).css("background-color",c.sectionsColor[a]);"undefined"!==typeof c.anchors[a]&&b(this).attr("data-anchor",c.anchors[a]);if(1<f){a=100*f;var g=100/f;e.wrapAll('<div class="fp-slidesContainer" />');e.parent().wrap('<div class="fp-slides" />');b(this).find(".fp-slidesContainer").css("width",a+"%");c.controlArrows&&pa(b(this));c.slidesNavigation&&ya(b(this),f);e.each(function(a){b(this).css("width",
g+"%");c.verticalCentered&&ka(b(this))});d=d.find(".fp-slide.active");0==d.length?e.eq(0).addClass("active"):J(d)}else c.verticalCentered&&ka(b(this))}).promise().done(function(){b.fn.fullpage.setAutoScrolling(c.autoScrolling,"internal");var a=b(".fp-section.active").find(".fp-slide.active");a.length&&(0!=b(".fp-section.active").index(".fp-section")||0==b(".fp-section.active").index(".fp-section")&&0!=a.index())&&J(a);c.fixedElements&&c.css3&&b(c.fixedElements).appendTo("body");c.navigation&&(k.css("margin-top",
"-"+k.height()/2+"px"),k.find("li").eq(b(".fp-section.active").index(".fp-section")).find("a").addClass("active"));c.menu&&c.css3&&b(c.menu).closest(".fullpage-wrapper").length&&b(c.menu).appendTo("body");c.scrollOverflow?("complete"===document.readyState&&R(),b(window).on("load",R)):b.isFunction(c.afterRender)&&c.afterRender.call(this);ha();a=window.location.hash.replace("#","").split("/")[0];if(a.length){var d=b('[data-anchor="'+a+'"]');!c.animateAnchor&&d.length&&(c.autoScrolling?n(d.position().top):
(n(0),D(a),b("html, body").scrollTop(d.position().top)),H(a,null),b.isFunction(c.afterLoad)&&c.afterLoad.call(this,a,d.index(".fp-section")+1),d.addClass("active").siblings().removeClass("active"))}b(window).on("load",function(){var a=window.location.hash.replace("#","").split("/"),b=a[0],a=a[1];b&&L(b,a)})});var T,U,F=!1;b(window).on("scroll",S);var v=0,B=0,u=0,A=0;b(window).on("hashchange",da);b(document).keydown(function(a){if(c.keyboardScrolling&&c.autoScrolling&&(40!=a.which&&38!=a.which||a.preventDefault(),
!m))switch(a.which){case 38:case 33:b.fn.fullpage.moveSectionUp();break;case 40:case 34:b.fn.fullpage.moveSectionDown();break;case 36:b.fn.fullpage.moveTo(1);break;case 35:b.fn.fullpage.moveTo(b(".fp-section").length);break;case 37:b.fn.fullpage.moveSlideLeft();break;case 39:b.fn.fullpage.moveSlideRight()}});b(document).on("click touchstart","#fp-nav a",function(a){a.preventDefault();a=b(this).parent().index();q(b(".fp-section").eq(a))});b(document).on("click touchstart",".fp-slidesNav a",function(a){a.preventDefault();
a=b(this).closest(".fp-section").find(".fp-slides");var c=a.find(".fp-slide").eq(b(this).closest("li").index());w(a,c)});c.normalScrollElements&&(b(document).on("mouseenter",c.normalScrollElements,function(){b.fn.fullpage.setMouseWheelScrolling(!1)}),b(document).on("mouseleave",c.normalScrollElements,function(){b.fn.fullpage.setMouseWheelScrolling(!0)}));b(".fp-section").on("click touchstart",".fp-controlArrow",function(){b(this).hasClass("fp-prev")?b.fn.fullpage.moveSlideLeft():b.fn.fullpage.moveSlideRight()});
b(window).resize(ga);var M=h,ia;b.fn.fullpage.destroy=function(a){b.fn.fullpage.setAutoScrolling(!1,"internal");b.fn.fullpage.setAllowScrolling(!1);b.fn.fullpage.setKeyboardScrolling(!1);b(window).off("scroll",S).off("hashchange",da).off("resize",ga);b(document).off("click","#fp-nav a").off("mouseenter","#fp-nav li").off("mouseleave","#fp-nav li").off("click",".fp-slidesNav a").off("mouseover",c.normalScrollElements).off("mouseout",c.normalScrollElements);b(".fp-section").off("click",".fp-controlArrow");
a&&Aa()}}})(jQuery);