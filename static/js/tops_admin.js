/**
 * Created by taohe on 14-10-8.
 */
$(function() {
    var init = function() {
        initCondition();
    },
        initCondition = function() {
            $('.input-daterange').datepicker({
                format: 'yyyy-mm-dd'
            });
        };
    init();

});