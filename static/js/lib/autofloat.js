// Generated by CoffeeScript 1.8.0
(function() {
  define(['jquery', 'underscore'], function($, _) {
    var element, parent, parentHeight, scrollTimeout, selfHeight, setTop;
    element = $('*[data-role=float]');
    parent = element.parent().parent();
    element.parent().css('position', 'relative');
    parentHeight = parent.height() - 15;
    selfHeight = element.height();
    element.css('width', element.width());
    scrollTimeout = null;
    setTop = function() {
      var parentTop, scrollTop;
      if (!element || selfHeight >= parentHeight) {
        return;
      }
      scrollTop = $(window.document).scrollTop();
      parentTop = parent.offset().top;
      element.css('position', 'absolute');
      if (scrollTop < parentTop + 15) {
        return element.animate({
          top: 0
        });
      } else if (scrollTop - parentTop + selfHeight <= parentHeight) {
        return element.animate({
          top: scrollTop - parentTop - 15
        });
      } else if (scrollTop - parentTop + selfHeight > parentHeight) {
        return element.animate({
          top: parentHeight - selfHeight
        });
      }
    };
    return $(window.document).scroll(function(e) {
      if (scrollTimeout) {
        clearTimeout(scrollTimeout);
        scrollTimeout = null;
      }
      return scrollTimeout = setTimeout(setTop, 100);
    });
  });

}).call(this);
