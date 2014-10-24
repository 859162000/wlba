/**
 * Created by taohe on 14-10-8.
 */
$(function() {
    var init = function() {
        var categories = [], joined = [], trade = [], amount = [];
        var getNum = function(num) {
            return num ? parseFloat(num) : 0;
        };
        for(var key in result) {
            categories.push(result[key].each_day);
            joined.push(result[key].joined_num || 0);
            trade.push(result[key].trade_num || 0);
            amount.push(getNum(result[key].amount));
        }
        drawChart({categories: categories, joined: joined, trade: trade, amount: amount});
        initCondition();
    },
        drawChart = function(result) {
            $('#container').highcharts({
                title: {
                    text: '网利宝每日运营数据',
                    x: -20 //center
                },
                subtitle: {
                    text: 'Source: wanglibao.com',
                    x: -20
                },
                xAxis: {
                    categories: result.categories,
                    labels: {
                        rotation: 45
                    }
                },
                yAxis: {
                    title: {
                        text: '量'
                    },
                    plotLines: [{
                        value: 0,
                        width: 1,
                        color: '#808080'
                    }]
                },
                tooltip: {
                    valueSuffix: ''
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle',
                    borderWidth: 0
                },
                series: [{
                    name: '注册数',
                    data: result.joined
                }, {
                    name: '新增交易数',
                    data: result.trade
                }, {
                    name: '新增交易额',
                    data: result.amount
                }]
            });
        },
        initCondition = function() {
            $('.input-daterange').datepicker({
            });
        };
    init();

});