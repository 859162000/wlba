var dataVal;//数据
// 路径配置
require.config({
    paths: {
        echarts: './echarts',
        zrender: './echarts/zrender'
    }
});
require(["jquery"],function($){
    $.ajax({
        type: "get",
        url: "/api/datacube/",
        dataType: "json",
        success: function(data){
            //console.log(data.result);
            dataVal = data.result;
            allFun();
        }
    });
});
function getSortFun(order, sortBy){//json对象数组按对象属性排序
    var ordAlpah = (order == 'asc') ? '>' : '<';
    var sortFun = new Function('a', 'b', 'return a.' + sortBy + ordAlpah + 'b.' + sortBy + '?1:-1');
    return sortFun;
}
//数据 type
function typeData(amount){//s:开始索引值，e:结束索引值
    var val = []; //月份
    var num = []; //投资
    for(var i=0; i<amount.length; i++){
        val.push(amount[i].type);
        num.push(parseFloat(amount[i].QTY.replace(/,/g,"")));
    }
    return {"val": val, "num": num};
}
Array.prototype.arrSum = function(){//数组求和
    var sum = 0;
    for(var i = 0; i < this.length; i++){
        sum = sum + parseInt(this[i]);
    }
    return sum;
};
function percentNum(n,t){//求百分比（不带%）
    return ((n/t)*100).toFixed(2);
}
function fmoney(s, n) {//数字格式化，保留n位小数，如10000格式化为10,000
    n = n > 0 && n <= 20 ? n : 2;
    s = parseFloat((s + "").replace(/[^\d\.-]/g, "")).toFixed(n) + "";
    var l = s.split(".")[0].split("").reverse(), r = s.split(".")[1];
    var t = "";
    for (var i = 0; i < l.length; i++) {
        t += l[i] + ((i + 1) % 3 == 0 && (i + 1) != l.length ? "," : "");
    }
    return t.split("").reverse().join("") + "." + r;
}
function tabChange(nav, cont, obj){
    for(var j = 0; j<nav.length; j++){
        if(nav[j] === obj){
            if(nav[j].className.indexOf("active") > -1){
                return;
            }else{
                nav[j].className = nav[j].className + " active";
                cont[j].className = cont[j].className + " active";
            }
        }else{
            nav[j].className = nav[j].className.replace(/ active/g,"");
            cont[j].className = cont[j].className.replace(/ active/g,"");
        }
    }
}
function tabFun(n, c){ //tab切换
    var nav = document.getElementById(n).getElementsByTagName("li");
    var cont = document.getElementById(c).getElementsByTagName("li");
    if(nav.length != cont.length){
        return;
    }
    for(var i=0; i<nav.length; i++){
        nav[i].onclick = function(){
            tabChange(nav, cont, this);
        }
    }
}
function getBeforeDate(t,n){//获取某时间的前n天,t：某时间
  t = t.replace(/-/g,"/");
  var d = new Date(t);
  var year = d.getFullYear();
  var mon = d.getMonth()+1;
  var day = d.getDate();
  var s;
  if(day <= n){
    if(mon > 1) {
      mon = mon-1;
    }else {
      year = year-1;
      mon = 12;
    }
  }
  d.setDate(d.getDate()-n);
  mon = d.getMonth()+1;
  day = d.getDate();
  s = year+"-"+(mon<10?('0'+mon):mon)+"-"+(day<10?('0'+day):day);
  return s;
}

function allFun(){
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
        //数据
        var mouthAmount = dataVal.month_amount;
        var mouthNum = []; //月份
        var mouthVal = []; //投资
        if(mouthAmount.length < 22){
            for(var i=4; i<mouthAmount.length; i++){
                mouthNum.push(mouthAmount[i].date.replace(/-/g,"."));
                mouthVal.push(mouthAmount[i].invest.replace(/,/g,""));
            }
        }else{
            for(var i=4; i<mouthAmount.length; i++){
                var month = mouthAmount[i].date.substr(mouthAmount[i].date.length-2,2);
                if(month == "01"){
                    month = mouthAmount[i].date.replace(/-/g,".");
                }
                mouthNum.push(month);
                mouthVal.push(mouthAmount[i].invest.replace(/,/g,""));
            }
        }

        document.getElementById("close-date").innerText = dataVal.plat_total[0].date;//截止日期
        function setNum(id,v){ //设置平台数据总值
            var arr = v.split(".");
            id.innerHTML = arr[0] + '<span class="font-l">.' + arr[1] + '</span>';
        }
        //总数据
        var plat_total = dataVal.plat_total.sort(getSortFun('asc', "type"));
        setNum(document.getElementById('match-num'), plat_total[0].Qty);
        setNum(document.getElementById('paid-num'), plat_total[2].Qty);
        setNum(document.getElementById('expect-num'), plat_total[4].Qty);
        setNum(document.getElementById('put-out-num'), plat_total[6].Qty);

        //平台7日数据
        document.getElementById('data-days7').innerHTML = "（"+ getBeforeDate(dataVal.plat_total[4].date,6).replace(/-/g,".") + " - " + dataVal.plat_total[4].date.replace(/-/g,".")  + ")";
        document.getElementById('match-num7').innerHTML = plat_total[1].Qty;
        document.getElementById('paid-num7').innerHTML = plat_total[3].Qty;
        document.getElementById('expect-num7').innerHTML = plat_total[5].Qty;
        document.getElementById('put-out-num7').innerHTML = plat_total[7].Qty;

        var option = {
            color: ['#9ab5e8'],
            tooltip: {
                show: true,
                backgroundColor: 'rgba(255,255,255,1)',
                textStyle: {
                    color: '#477ced'
                },
                formatter: '￥{c}'
            },
            calculable: true,
            grid: {
                borderWidth: 0
            },
            xAxis : [
                {
                    type : 'category',
                    data: mouthNum,
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
                        interval: 0,
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
                    name: "（单位：元）",
                    type : 'value',
                    min: 0,
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
                    barWidth: 35,//柱形宽度
                    "data": mouthVal,
                    itemStyle: {
                        normal : {
                            barBorderRadius: [8,8,0,0]
                        },
                        emphasis :{
                            barBorderRadius: [8,8,0,0]
                        }
                    }
                }
            ]
        };
        // 为echarts对象加载数据
        myChart.setOption(option);

        //年龄 数据
        var ageArr = typeData(dataVal.age);
        var ageTotal = ageArr.num.arrSum();
        //投资人年龄分布
        optiondb = {
            toolbox: {
                show : false
            },
            color: ['#9ab5e8'],
            tooltip: {
                show: true,
                formatter: '{c}%'
            },
            calculable : true,
            grid: {borderWidth: 0},
            xAxis : [
                {
                    type : 'category',
                    data : [ageArr.val[0],ageArr.val[1],ageArr.val[2],ageArr.val[3],ageArr.val[4],ageArr.val[5]],
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
                    data : [ageArr.val[0],ageArr.val[1],ageArr.val[2],ageArr.val[3],ageArr.val[4],ageArr.val[5]]
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
                    data:[percentNum(ageArr.num[0],ageTotal),percentNum(ageArr.num[1],ageTotal),percentNum(ageArr.num[2],ageTotal),percentNum(ageArr.num[3],ageTotal),percentNum(ageArr.num[4],ageTotal),percentNum(ageArr.num[5],ageTotal)]
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
                    data:[100,100,100,100,100,100,100]
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
    var pie1_data, pie2_data, pie3_data, pie4_data;
    var sex_data;//投资人性别分布
    var channel_data; //投资渠道分布
    var sexDom = ec.init(document.getElementById('cube-sex'));
    var cDom = ec.init(document.getElementById('cube-channel'));

    function setOpt(cfg,or,x){//融资概览
        if(or == undefined){
            or = "horizontal";
        }
      var option = {
        color: ['#d5dfdd','#94b0e3','#f29894','#93d1b3','#fcce8c','#f6ec8c',"#b3e1dd","#d193c6"],
        tooltip : {
            formatter: "{d}%"
        },
        legend: {
            orient : or,
            y : 250,
            x: x,
            itemGap: 12,
            data:cfg.legendData
        },
        calculable : true,
        series : [
            {
                name:cfg.name,
                type:'pie',
                radius : ['50%', '70%'],
                center: [ '50%', 125 ],
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
                    {value:cfg.itemDate[5], name:cfg.legendData[5]},
                    {value:cfg.itemDate[6], name:cfg.legendData[6]},
                    {value:cfg.itemDate[7], name:cfg.legendData[7]}
                ]
            }
        ]
      };
      return option;
    }

    pie1_data = typeData(dataVal.times);//融资期限
    pie2_data = typeData(dataVal.amount);//融资金额
    pie3_data = typeData(dataVal.type);//融资类型
    pie4_data = typeData(dataVal.way);//还款方式
    //整理融资金额/融资类型的排序
    var pie2_data_r = {"val": [pie2_data.val[4],pie2_data.val[2],pie2_data.val[1],pie2_data.val[3],pie2_data.val[0]], "num": [pie2_data.num[4],pie2_data.num[2],pie2_data.num[1],pie2_data.num[3],pie2_data.num[0]]};
    var pie3_data_r = {"val": [pie3_data.val[0],pie3_data.val[2],pie3_data.val[3],pie3_data.val[4],pie3_data.val[5],pie3_data.val[6],pie3_data.val[7],pie3_data.val[1]], "num": [pie3_data.num[0],pie3_data.num[2],pie3_data.num[3],pie3_data.num[4],pie3_data.num[5],pie3_data.num[6],pie3_data.num[7],pie3_data.num[1]]};
    // 为echarts对象加载数据
    pie1.setOption(setOpt({'name':'融资期限','legendData': pie1_data.val, "itemDate": pie1_data.num},"vertical",30));
    pie2.setOption(setOpt({'name':'融资金额','legendData': pie2_data_r.val, "itemDate": pie2_data_r.num},"vertical",30));
    pie3.setOption(setOpt({'name':'融资类型','legendData': pie3_data_r.val, "itemDate": pie3_data_r.num},"vertical",30));
    pie4.setOption(setOpt({'name':'还款方式','legendData': pie4_data.val, "itemDate": pie4_data.num},"vertical","center"));

    function setSex(cfg){//投资人性别分布&投资渠道分布
        var opt = {
            color: cfg.colorVal,
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {d}%"
            },
            legend: {
                orient : 'horizontal',
                x : 'center',
                y: "bottom",
                data: cfg.legend
            },
            toolbox: {
                show : false
            },
            calculable : false,
            series : [
                {
                    name: cfg.name,
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
                                show : false,
                                position : 'inner'
                            },
                            labelLine : {
                                show : false
                            }
                        }
                    },
                    data:[
                        {value:cfg.value[0], name:cfg.legend[0], selected:true},
                        {value:cfg.value[1], name:cfg.legend[1]},
                        {value:cfg.value[2], name:cfg.legend[2]}
                    ]
                }
            ]
        }
        return opt;
    }
    sex_data = typeData(dataVal.sex);
    channel_data = typeData(dataVal.invest_terminal);
    sexDom.setOption(setSex({"name":"投资人性别分布", "colorVal":['#4bb281','#e9534d'], "legend":[sex_data.val[2], sex_data.val[0]], "value": [sex_data.num[2], (sex_data.num[0]+sex_data.num[1])]}));
    cDom.setOption(setSex({"name":"投资人渠道分布", "colorVal":['#4d7bd0','#ef8048'], "legend":['PC','APP'], "value": [(channel_data.num[1] - channel_data.num[0]),channel_data.num[0]]}));
});
require(['echarts','echarts/chart/map'],function(ec) {//地图
    tabFun("map-tab-nav", "map-tab-cont"); //tab切换
    var map1 = ec.init(document.getElementById('map-img1'));
    var map2 = ec.init(document.getElementById('map-img2'));
    function setMap(cfg){
        var option = {
            tooltip : {
                trigger: 'item',
                formatter: '{b}:{c}'
            },
            series : [
                {
                    name: '中国',
                    type: 'map',
                    mapType: 'china',
                    mapLocation: {
                      x: 'left',
                      y: 'center'
                    },
                    itemStyle:{
                        normal:{
                            borderWidth: 1,
                            borderColor:'#fff',
                            label:{show:true,textStyle: {color: "#999"}},
                            areaStyle:{color:'#dadee6'}
                        },
                        emphasis:{
                            borderWidth: 1,
                            borderColor:'#fff',
                            label:{show:true,textStyle: {color: "#fff"}},
                            color:"#4d7bd0"
                        }
                    },
                    data: cfg
                }
            ],
            dataRange: {
                show: false,
                splitList: [
                    {start:cfg[0].value, end:cfg[0].value, label: cfg[0].name, color: '#e8403a'}, //1
                    {start:cfg[1].value, end:cfg[1].value, label: cfg[1].name, color: '#f06824'}, //2
                    {start:cfg[2].value, end:cfg[2].value, label: cfg[2].name, color: '#f2bf18'} //3
                ]
            }
        };
        return option;
    }

    function mapNum(){ //h:是否取消"，",true：不取消
        var mapTotal = dataVal.china_map;
        var mapPrice = [],
            mapPeople = [];
        for(var i=0; i<mapTotal.length; i++){
            mapPrice.push({"name": mapTotal[i].province.replace(/(^\s*)|(\s*$)/g,""), "value": parseFloat(mapTotal[i].invest_amount.replace(/,/g,""))});
            mapPeople.push({"name": mapTotal[i].province.replace(/(^\s*)|(\s*$)/g,""), "value": parseFloat(mapTotal[i].investor.replace(/,/g,""))});
        }
        return {"price": mapPrice, "people": mapPeople};
    }

    var map_data = mapNum();
    var map_data1 = map_data.price.sort(getSortFun('desc', 'value'));
    var map_data2 = map_data.people.sort(getSortFun('desc', 'value'));
    map1.setOption(setMap(map_data1));
    map2.setOption(setMap(map_data2));

    function mapTop10(arr,d){
        var str = "";
        for(var i = 0; i<10; i++){
           str += '<p class="map-list-item"><span class="map-num map-num'+ (i+1) +'">'+ (i+1) +'</span>'+ arr[i].name + '： <span class="font-color9">'+ fmoney(arr[i].value, 2) + d + '</span></span></p>'
        }
        return str;
    }
    document.getElementById("map1-list").innerHTML = mapTop10(map_data1,"元");
    document.getElementById("map2-list").innerHTML = mapTop10(map_data2,"人");
});
}
//大事记
;(function(){
    var dom = document.getElementById("event-list");
    var events = {
        prve: document.getElementById("event-prve"),
        next: document.getElementById("event-next"),
        dom:  dom,
        liDom: dom.getElementsByTagName("li"),
        setFun: "",
        animate: false,
        setVal: function(){
            var lft = events.dom.offsetLeft;
			var liw = events.liDom[0].style.width || events.liDom[0].offsetWidth;
			var tw = events.liDom.length * liw;
			if(lft === ''){
				lft = 0;
			}else{
				lft = parseInt(lft);
			}
			return {"marginLeft": lft,"liWidth": liw, "totalWidth": tw};
        },
        _scroll: function(val,h){
            if(events.animate){
				return;
			}
			var arr = events.setVal();
			var i = 0;
			if((h === "+" && arr.marginLeft >= val) || (h === "-" && arr.marginLeft <= val)){
				return;
			}else{
                if(h === "+" && arr.marginLeft >= (val - arr.liWidth)){
                    events.prve.style.display = "none";
                }else if(h === "-" && arr.marginLeft <= (val+arr.liWidth)){
                    events.next.style.display = "none";
                }
				events.animate = true;
				events.setFun = setInterval(function(){
					if(i >= arr.liWidth){
						clearInterval(events.setFun);
						events.animate = false;
					}
					if(h === "+"){
                        events.next.style.display = "block";
						events.dom.style.left = (arr.marginLeft + i) + "px";
					}else{
                        events.prve.style.display = "block";

						events.dom.style.left = (arr.marginLeft - i) + "px";
					}
					i = i+40;
				},10);
			}
        }
    }
    //设置大事记ul宽度
	events.dom.style.width = events.setVal().totalWidth+"px";
    //左
    events.prve.onclick = function(){
        events._scroll(0,"+");
	}
    //右
    events.next.onclick = function(){
        var arr = events.setVal();
        var pDom = events.dom.parentNode;
        var pw = pDom.style.width || pDom.offsetWidth;
        events._scroll((-arr.totalWidth+pw),"-");
    }
})();
