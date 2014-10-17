// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      'jquery': 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    $('.list-container').on('click', '.list-item-title', function(e) {
      var item;
      item = $(this).parent();
      if (item.hasClass('active')) {
        return;
      }
      $('.list-item').removeClass('active');
      item.addClass('active');
    });
    $('.help-menu').on('click', 'li', function(e) {
      var source, tar;
      e.preventDefault();
      if ($(this).hasClass('current')) {
        return;
      }
      $('.help-menu li.current').removeClass('current');
      $(this).addClass('current');
      $('.help-box').removeClass('active');
      $('.list-item').removeClass('active');
      tar = $(this);
      source = $('.help-box[data-source="' + tar.attr('data-target') + '"]');
      source.addClass('active');
      return $('.list-item:eq(0)', source).addClass('active');
    });
    $('.hot-items').on('click', 'li', function(e) {
      var contentId, item, menu, topic, topicId;
      e.preventDefault();
      topicId = $('a', $(this)).attr('data-topic');
      contentId = $('a', $(this)).attr('data-item');
      topic = $('.help-box[data-source="' + topicId + '"]');
      item = $('.list-item[data-source="' + contentId + '"]', topic);
      menu = $('.help-menu li[data-target="' + topicId + '"]');
      $('.help-menu li.current').removeClass('current');
      menu.addClass('current');
      $('.help-box').removeClass('active');
      $('.list-item').removeClass('active');
      topic.addClass('active');
      return item.addClass('active');
    });
    return $(window).load(function(e) {
      var source, tar;
      tar = $('.help-menu li:eq(0)');
      tar.addClass('current');
      source = $('.help-box[data-source="' + tar.attr('data-target') + '"]');
      source.addClass('active');
      return $('.list-item:eq(0)', source).addClass('active');
    });
  });

}).call(this);

//# sourceMappingURL=help.map
