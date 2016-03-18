require.config({
    paths: {
        'picker': 'lib/picker',
        'picker.date': 'lib/picker.date',
    },
    shim: {
        'picker.date': ['jquery'],
        'picker': ['jquery']
    }
});

require(['jquery', 'picker', 'picker.date'], function ($) {
    $.extend($.fn.pickadate.defaults, {
        format: 'yyyy-mm-dd',
        formatSubmit: 'yyyy-mm-dd',
        monthsFull: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
        monthsShort: ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'],
        weekdaysFull: ['一', '二', '三', '四', '五', '六', '七'],
        weekdaysShort: ['一', '二', '三', '四', '五', '六', '七'],
        //selectMonths: true,
        selectYears: true,
        today: '今天',
        clear: '清除',
        close: '关闭',
    });

    $('.start-date').pickadate({
        hiddenPrefix: 'start'
    })
     $('.end-date').pickadate({
        hiddenPrefix: 'end'
    })
});