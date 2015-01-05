/**
 * Created by taohe on 15-01-05.
 */
$(function() {
    var top_modal,
        future_modal;
    var init = function() {
        initComponent();
    },
        showTopsOfDay = function(position, day) {
            var url = '/api/gettopofday/';
            renderData(url, day, function() {
                var n_position = getPosition(position, top_modal);
                top_modal.show();
                $('.title', top_modal).html('日排行');
                top_modal.css({'left': n_position.left+'px', 'top': n_position.top+'px'});
            }, function() {
                var n_position = getPosition(position, future_modal);
                future_modal.show();
                future_modal.css({'left': n_position.left+'px', 'top': n_position.top+'px'});
            });
        },
        showTopsOfWeek = function(position, week) {
            var url = '/api/gettopofweek/';
            renderData(url, week, function() {
                var n_position = getPosition(position, top_modal);
                top_modal.show();
                $('.title', top_modal).html('周排行');
                top_modal.css({'left': n_position.left+'px', 'top': n_position.top+'px'});
            }, function() {
                var n_position = getPosition(position, future_modal);
                future_modal.show();
                future_modal.css({'left': n_position.left+'px', 'top': n_position.top+'px'});
            });
        },
        hideTopOfDay = function() {
            top_modal.hide();
            $('.day-modal').hide();
        },
        renderData = function(url, day, callback, callback_future) {
            $.post(url, {day: day}, function(data) {
                if(data.ret_code == 0 && data.isvalid == 0) {
                    return;
                } else if(data.ret_code == 0 && data.records.length > 0) {
                   $('tbody', top_modal).html(createHtml(data.records))
                   callback.call(this)
                } else if(data.ret_code == 0 && data.isvalid == 1 && data.records.length == 0) {
                   //showFuture();
                   callback_future(this)
                }
            });
        },
        safe_phone = function(phone) {
          return phone.replace(/(\d{3})\d{6}(\d{2})/ig,'$1*****$2');
        },
        createHtml = function(records) {
            var i = 0,
                len = records.length,
                str = [];
            for(; i < len; i++) {
                str.push('<tr>')
                str.push('<td>');
                str.push(i+1);
                str.push('</td>')
                str.push('<td>');
                str.push(safe_phone(records[i].phone));
                str.push('</td>')
                str.push('<td>');
                str.push(records[i].amount_sum);
                str.push('</td>')
                str.push('</tr>')
            }
            return str.join('');
        },
        getPosition = function(position, modal) {
            var modal_position = {};
            modal_position.left = position.left - modal.width()/2 + 30,
            modal_position.top = position.top - modal.height() - 20;

            return modal_position;
        },
        initComponent = function() {
           $('.day-dot').mouseenter(function(e) {
               var self = $(this);

               showTopsOfDay(self.position(), self.attr('data-day'))
           });

           $('.day-dot').mouseleave(function(e) {
               hideTopOfDay()
           });


           $('.history-week-label').mouseenter(function(e) {
               var self = $(this);
               showTopsOfWeek(self.position(), self.attr('data-week'))
           });

           $('.history-week-label').mouseleave(function(e) {
               hideTopOfDay()
           });

           top_modal = $('#top_modal');
           future_modal = $('#future_modal');
        };
    init();

});