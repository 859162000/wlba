// 路径配置
require.config({
    paths: {
        echarts: './'
    }
});

// 使用
require(
    [
        'echarts',
        'echarts/chart/bar' // 使用柱状图就加载bar模块，按需加载
    ],
    function (ec) {
        // 基于准备好的dom，初始化echarts图表
        var myChart = ec.init(document.getElementById('data-total'));
        var age = ec.init(document.getElementById('cube-age'));
        var optiondb; //投资人年龄分布
        var option = {
            color: ['#9ab5e8'],
            tooltip: {
                show: true,
                backgroundColor: 'rgba(255,255,255,1)',
                textStyle: {
                    color: '#477ced'
                },
                formatter: function (params,ticket,callback) {
                    var res = '￥';
                     res += params[2];
                    return res;
                }
            },
            calculable: true,
            grid: {
                borderWidth: 0
            },
            xAxis : [
                {
                    type : 'category',
                    data : ["2014.12","2015.1","2015.2","2015.3","2015.4","2015.5","2015.6","2015.7","2015.8","2015.9","2015.10","2015.11"],
                    splitLine: {
                        show: false
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#d9d9d9',
                            width: 1
                        }
                    },
                    axisLabel: {
                        textStyle: {
                            color: "#fff"
                        }
                    },
                    axisTick: {
                        show: false
                    }
                }
            ],
            yAxis : [
                {
                    name: "（单位：万元）",
                    type : 'value',
                    min: 0,
                    max: 100,
                    splitNumber: 5,
                    splitLine: {
                        show: false
                    },
                    axisLabel: {
                        show: false
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#d9d9d9',
                            width: 1
                        }
                    }
                }
            ],
            series : [
                {
                    "type":"bar",
                    barWidth: 40,//柱形宽度
                    "data":[5, 20, 40, 10, 10, 20,5, 20, 40, 10, 10, 20],
                    itemStyle: {
                        normal : {
                            barBorderRadius: [10,10,0,0]
                        },
                        emphasis :{
                            barBorderRadius: [10,10,0,0]
                        }
                    }
                }
            ]
        };

        // 为echarts对象加载数据
        myChart.setOption(option);

        optiondb = {
            toolbox: {
                show : false
            },
            color: ['#9ab5e8'],
            tooltip: {
                show: true,
                formatter: function (params,ticket,callback) {
                    var res = params[2] + "%";
                    return res;
                }
            },
            calculable : true,
            grid: {borderWidth: 0},
            xAxis : [
                {
                    type : 'category',
                    data : ["0-19岁","20-29岁","30-39岁","40-49岁","50-59岁","60岁以上"],
                    //data : ["0-19岁","20-29岁","30-39岁","40-49岁","50-59岁","60岁以上"],
                    axisLine: {show:false},
                    splitLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    }
                },
                {
                    type : 'category',
                    axisLine: {show:false},
                    axisTick: {show:false},
                    axisLabel: {show:false},
                    splitArea: {show:false},
                    splitLine: {show:false},
                    data : ["0-19岁","20-29岁","30-39岁","40-49岁","50-59岁","60岁以上"]
                }
            ],
            yAxis : [
                {
                    type : 'value',
                    axisLabel:{show: false},
                    axisLine: {show:false},
                    splitLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    }
                }
            ],
            series : [
                {
                    name:'投资人年龄分布',
                    type:'bar',
                    barWidth: 30,//柱形宽度
                    itemStyle: {
                        normal : {
                            color:'#4d7bd0',
                            label:{show:false},
                            barBorderRadius: [5,5,0,0]
                        },
                        emphasis :{
                            barBorderRadius: [5,5,0,0]
                        }
                    },
                    data:[6,31,8,78,20,20]
                },
                {
                    name:'投资人年龄分布',
                    type:'bar',
                    barWidth: 30,//柱形宽度
                    xAxisIndex:1,
                    itemStyle: {
                        normal : {
                            color:'#e6eaf1',
                            label:{show:false},
                            barBorderRadius: [5,5,0,0]
                        },
                        emphasis :{
                            barBorderRadius: [5,5,0,0]
                        }
                    },
                    data:[100,100,100,100,100,100]
                }
            ]
        };
        age.setOption(optiondb);
    }
);
require(['echarts','echarts/chart/pie'],function(ec){//饼形图
    var pie1 = ec.init(document.getElementById('cube-survey-img1'));
    var pie2 = ec.init(document.getElementById('cube-survey-img2'));
    var pie3 = ec.init(document.getElementById('cube-survey-img3'));
    var pie4 = ec.init(document.getElementById('cube-survey-img4'));

    var sex;//投资人性别分布
    var channel; //投资渠道分布
    var sexDom = ec.init(document.getElementById('cube-age'));
    var cDom = ec.init(document.getElementById('cube-sex'));
    function setOpt(cfg){//融资概览
      var option = {
        color: ['#d5dfdd','#94b0e3','#f29894','#93d1b3','#fcce8c','#f6ec8c'],
        tooltip : {
            formatter: "{d}%"
        },
        legend: {
            orient : 'horizontal',
            y : 270,
            x: 30,
            data:cfg.legendData
        },
        calculable : true,
        series : [
            {
                name:cfg.name,
                type:'pie',
                radius : ['50%', '70%'],
                center: [ '50%', 135 ],
                itemStyle : {
                    normal : {
                        label : {
                            show : false
                        },
                        labelLine : {
                            show : false
                        }
                    },
                    emphasis : {
                        label : {
                            show : false
                        }
                    }
                },
                data:[
                    {value:cfg.itemDate[0], name:cfg.legendData[0]},
                    {value:cfg.itemDate[1], name:cfg.legendData[1]},
                    {value:cfg.itemDate[2], name:cfg.legendData[2]},
                    {value:cfg.itemDate[3], name:cfg.legendData[3]},
                    {value:cfg.itemDate[4], name:cfg.legendData[4]},
                    {value:cfg.itemDate[5], name:cfg.legendData[5]}
                ]
            }
        ]
      };
      return option;
    }

    // 为echarts对象加载数据
    pie1.setOption(setOpt({'name':'融资期限','legendData':['小于1个月','3个月    ','1个月       ','6个月','2个月       ','其它'],"itemDate":[335,310,234,135,1000,548]}));
    pie2.setOption(setOpt({'name':'融资金额','legendData':['5万以下     ','50-100万之间','5-20万之间','100万以上','20-50万之间'],"itemDate":[335,310,234,135,1548]}));
    pie3.setOption(setOpt({'name':'融资类型','legendData':['车辆抵押借款','房产抵押贷','车辆融资借款','艺品贷','企业资金周转','黄金宝'],"itemDate":[335,310,234,135,1000,548]}));
    pie4.setOption(setOpt({'name':'还款方式','legendData':['等额本息 ','按月付息，到期还本','一次性还本付息'],"itemDate":[335,310,234]}));

    function setSex(){//投资人性别分布&投资渠道分布
        var opt = {
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            legend: {
                orient : 'vertical',
                x : 'left',
                data:['直达','营销广告','搜索引擎','邮件营销','联盟广告','视频广告','百度','谷歌','必应','其他']
            },
            toolbox: {
                show : true,
                feature : {
                    mark : {show: true},
                    dataView : {show: true, readOnly: false},
                    magicType : {
                        show: true,
                        type: ['pie', 'funnel']
                    },
                    restore : {show: true},
                    saveAsImage : {show: true}
                }
            },
            calculable : false,
            series : [
                {
                    name:'访问来源',
                    type:'pie',
                    selectedMode: 'single',
                    radius : [0, 70],

                    // for funnel
                    x: '20%',
                    width: '40%',
                    funnelAlign: 'right',
                    max: 1548,

                    itemStyle : {
                        normal : {
                            label : {
                                position : 'inner'
                            },
                            labelLine : {
                                show : false
                            }
                        }
                    },
                    data:[
                        {value:335, name:'直达'},
                        {value:679, name:'营销广告'},
                        {value:1548, name:'搜索引擎', selected:true}
                    ]
                }
            ]
        }
    }
    sexDom.setOption(setSex());
});