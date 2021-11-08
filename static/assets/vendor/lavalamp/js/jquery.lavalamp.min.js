/*!
 * Lava Lamp
 * http://lavalamp.magicmediamuse.com/
 *
 * Author
 * Richard Hung
 * http://www.magicmediamuse.com/
 *
 * Version
 * 1.1.0
 * 
 * Copyright (c) 2014 Richard Hung.
 * 
 * License
 * Lava Lamp by Richard Hung is licensed under a Creative Commons Attribution-NonCommercial 3.0 Unported License.
 * http://creativecommons.org/licenses/by-nc/3.0/deed.en_US
 */


!function(a){"use strict";var t={init:function(t){var o={easing:"ease",duration:700,margins:!1,setOnClick:!1,activeObj:".active",autoUpdate:!1,updateTime:100,enableHover:!0,delayOn:0,delayOff:0,enableFocus:!1,deepFocus:!1};return t=a.extend({},o,t),this.each(function(){var o=t.margins,s=t.setOnClick,m=t.activeObj,r=t.autoUpdate,p=t.updateTime,u=t.enableHover,v=t.delayOn,c=t.delayOff,d=t.enableFocus,f=t.deepFocus,h=t.duration,g=t.easing,b=a(this),T=b.children(),y=b.children(m);0===y.length&&(y=T.eq(0)),b.addClass("lavalamp").data({lavalampActive:y,isAnim:!1,settings:t});var A=a('<div class="lavalamp-object '+g+'" />').prependTo(b);T.addClass("lavalamp-item"),A.css({WebkitTransitionDuration:h/1e3+"s",msTransitionDuration:h/1e3+"s",MozTransitionDuration:h/1e3+"s",OTransitionDuration:h/1e3+"s",transitionDuration:h/1e3+"s"});var j=y.outerWidth(o),I=y.outerHeight(o),O=y.position().top,C=y.position().left,x=y.css("marginTop"),D=y.css("marginLeft");o||(D=parseInt(D),x=parseInt(x),C+=D,O+=x),A.css({width:j,height:I,transform:"translate("+C+"px,"+O+"px)"});var F=!1,H=!0;if(e=function(){var t=a(this);F=!0,setTimeout(function(){F&&H&&b.lavalamp("anim",t)},v)},i=function(a){a=b.data("lavalampActive"),F=!1,setTimeout(function(){!F&&H&&b.lavalamp("anim",a)},c)},n=function(){var t=a(this);t.hasClass("lavalamp-item")||(t=t.parents(".lavalamp-item")),H=!1,setTimeout(function(){b.lavalamp("anim",t)},v)},l=function(){H=!0;var a=b.data("lavalampActive");setTimeout(function(){b.lavalamp("anim",a)},c)},u&&(b.on("mouseenter",".lavalamp-item",e),b.on("mouseleave",".lavalamp-item",i)),d&&(b.on("focusin",".lavalamp-item",n),b.on("focusout",".lavalamp-item",l)),f&&(b.on("focusin",".lavalamp-item *",n),b.on("focusout",".lavalamp-item *",l)),s&&T.click(function(){y=a(this),b.data("lavalampActive",y).lavalamp("update")}),r){var k=setInterval(function(){var a=b.data("isAnim");F||a||b.lavalamp("update")},p);b.data("updateInterval",k)}})},destroy:function(){return this.each(function(){var t=a(this),o=t.data("settings"),s=t.children(".lavalamp-item"),m=o.enableHover,r=o.enableFocus,p=o.deepFocus,u=o.autoUpdate;if(m&&(t.off("mouseenter",".lavalamp-item",e),t.off("mouseleave",".lavalamp-item",i)),r&&(t.off("focusin",".lavalamp-item",n),t.off("focusout",".lavalamp-item",l)),p&&(t.off("focusin",".lavalamp-item *",n),t.off("focusout",".lavalamp-item *",l)),t.removeClass("lavalamp"),s.removeClass("lavalamp-item"),u){var v=t.data("updateInterval");clearInterval(v)}t.children(".lavalamp-object").remove(),t.removeData()})},update:function(){return this.each(function(){var t=a(this),e=t.children(":not(.lavalamp-object)"),i=t.data("lavalampActive");e.addClass("lavalamp-item").css({zIndex:5,position:"relative"}),t.lavalamp("anim",i)})},anim:function(a){var t=this,e=t.data("settings"),i=e.duration,n=e.margins,l=t.children(".lavalamp-object"),o=a.outerWidth(n),s=a.outerHeight(n),m=a.position().top,r=a.position().left,p=a.css("marginTop"),u=a.css("marginLeft");n||(u=parseInt(u),p=parseInt(p),r+=u,m+=p),t.data("isAnim",!0),l.css({width:o,height:s,transform:"translate("+r+"px,"+m+"px)"}),setTimeout(function(){t.data("isAnim",!1)},i)}};a.fn.lavalamp=function(e){return t[e]?t[e].apply(this,Array.prototype.slice.call(arguments,1)):"object"!=typeof e&&e?void a.error("Method "+e+" does not exist on jQuery.lavalamp"):t.init.apply(this,arguments)};var e,i,n,l}(jQuery);