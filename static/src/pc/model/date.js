    define(['jquery', 'picker', 'picker.date'], function ($) {
        $.extend($.fn.pickadate.defaults, {
            format: 'yyyy-mm-dd',
            formatSubmit: 'yyyy-mm-dd',
            monthsFull: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
            monthsShort: ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'],
            weekdaysFull: ['一', '二', '三', '四', '五', '六', '七'],
            weekdaysShort: ['一', '二', '三', '四', '五', '六', '七'],
            selectYears: 3,
            today: '今天',
            clear: '清除',
            close: '关闭',
        });

        var filterDate = new Date(),
            year = filterDate.getFullYear(),
            month = filterDate.getMonth() + 1,
            day = filterDate.getDate(),
            $startDate = $('#start-date'),
            $endDate = $('#end-date');

        $startDate.attr('value', year + '-' + initMonth(month - 1) + '-'+ day)
        $endDate.attr('value', year + '-' + initMonth(month) + '-'+ day)
        function initMonth(month){

            if(month && month < 10){
                return '0'+ month
            }
            return month
        }
    });