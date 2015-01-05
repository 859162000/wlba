/**
 * Created by taohe on 14-10-8.
 */
$(function() {
    var init = function() {
        initComponent();
    },
        showTopsOfDay = function(result) {
        },
        initComponent = function() {
           $('.day-dot').mouseenter(function(e) {
               var self = $(this);

               console.log(self.position());

               showTopsOfDay()

           });
        };
    init();

});