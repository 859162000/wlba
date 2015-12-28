var dataVal;//数据
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

// 路径配置
require.config({
    paths: {
        echarts: '/static/scripts/app/echarts'
    }
});

function getSortFun(order, sortBy){//json对象数组按对象属性排序
    var ordAlpah = (order == 'asc') ? '>' : '<';
    var sortFun = new Function('a', 'b', 'return a.' + sortBy + ordAlpah + 'b.' + sortBy + '?1:-1');
    return sortFun;
}

function arrSum(arr,start,end){//数组求和（value）
    var sum = 0;
    if(!start){
      start = 0;
    }
    if(!end){
      end = arr.length;
    }
    for(var i = start; i < end; i++){
        sum = sum + parseInt(arr[i].value);
    }
    return sum;
};
function arrSumQTY(arr,start,end){//数组求和(QTY)
    var sum = 0;
    if(!start){
      start = 0;
    }
    if(!end){
      end = arr.length;
    }
    for(var i = start; i < end; i++){
        sum = sum + parseFloat(arr[i].QTY.replace(/,/g,""));
    }
    return sum;
};
function percentNum(n,t){//求百分比（不带%）
    return ((parseFloat(n)/parseFloat(t))*100).toFixed(2);
}
function numDivision(n,t,f){//除法
    if(!f && f !== 0){
       f = 1;
    }
    var num = parseFloat(n.replace(/,/g,""))/parseFloat(t);
    if(f > 0){
       num = num.toFixed(f);
    }else{
        num = Math.round(num);
    }
    return num;
}
function fmoney(s, num) {//数字格式化，保留n位小数，如10000格式化为10,000
    var n = num > 0 && num <= 20 ? num : 2;
    s = parseFloat((s + "").replace(/[^\d\.-]/g, "")).toFixed(n) + "";
    var l = s.split(".")[0].split("").reverse(), r = s.split(".")[1];
    var t = "";
    for (var i = 0; i < l.length; i++) {
        t += l[i] + ((i + 1) % 3 == 0 && (i + 1) != l.length ? "," : "");
    }
    if(num === 0){
        return t.split("").reverse().join("");
    }else{
        return t.split("").reverse().join("") + "." + r;
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
function setMap(){//设置地图
    require(['echarts','echarts/chart/map'],function(ec) {//地图
        var map1 = ec.init($('.map-main')[0]);
        var map2;
        if($('.map-main')[1]){
            map2 = ec.init($('.map-main')[1]);
        }
        function setMap(cfg){
            var option = {
                tooltip : {
                    show: false,
                    trigger: 'item',
                    formatter: '{b}:{c}'
                },
                series : [
                    {
                        name: '中国',
                        type: 'map',
                        mapType: 'china',
                        itemStyle:{
                            normal:{
                                borderWidth: 1,
                                borderColor:'#37498f',
                                label:{show:false,textStyle: {color: "#999"}},
                                areaStyle:{color:'#2a2b54'}
                            },
                            emphasis:{
                                borderWidth: 1,
                                borderColor:'#37498f',
                                label:{show:false,textStyle: {color: "#fff"}},
                                color:"#4d7bd0"
                            }
                        },
                        data: cfg
                    }
                ],
                dataRange: {
                    show: false,
                    splitList: [
                        {start:cfg[0].value, end:cfg[0].value, label: cfg[0].name, color: '#ff3a1a'}, //1
                        {start:cfg[1].value, end:cfg[1].value, label: cfg[1].name, color: '#ff581a'}, //2
                        {start:cfg[2].value, end:cfg[2].value, label: cfg[2].name, color: '#ffab1a'}, //3
                        {start:cfg[3].value, end:cfg[3].value, label: cfg[3].name, color: '#16b86a'}, //4
                        {start:cfg[4].value, end:cfg[4].value, label: cfg[4].name, color: '#762ffa'}, //5
                        {start:cfg[5].value, end:cfg[5].value, label: cfg[5].name, color: '#ff7a66'}, //6
                        {start:cfg[6].value, end:cfg[6].value, label: cfg[6].name, color: '#ffc766'}, //7
                        {start:cfg[7].value, end:cfg[7].value, label: cfg[7].name, color: '#5cb88b'}, //8
                        {start:cfg[8].value, end:cfg[8].value, label: cfg[8].name, color: '#b996fa'} //9
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
        var map_data1 = map_data.people.sort(getSortFun('desc', 'value'));
        map1.setOption(setMap(map_data1));
        if(map2){
           map2.setOption(setMap(map_data1));
        }
        function mapTop10(arr){
            var str = "";
            var barWidth = 100;
            var maxNum = arr[0].value;
            var totalNum = arrSum(map_data1);
            for(var i = 0; i<9; i++){
                barWidth = percentNum(arr[i].value,maxNum);
                str += '<div class="map-item map-item'+(i+1)+'">';
                str += '<div class="map-name tit18">'+ arr[i].name +'：</div>';
                str += '<div class="map-bar"><div class="map-bar-box has-an"><div class="bar-box" style="width:'+ barWidth +'%;"></div></div></div>';
                str += '<div class="map-num tit20">'+ percentNum(arr[i].value,totalNum) +'%</div>';
                str += '</div>';
                //str += '<p class="map-list-item"><span class="map-num map-num'+ (i+1) +'">'+ (i+1) +'</span>'+ arr[i].name + '： <span class="font-color9">'+ fmoney(arr[i].value, n) + d + '</span></span></p>'
            }
            str += '<div class="map-item map-item10">';
            str += '<div class="map-name tit18">其他：</div>';
            str += '<div class="map-bar"><div class="map-bar-box has-an"><img src="/static/imgs/app/data_cube/map-other.png" /></div></div>';
            str += '<div class="map-num tit20">'+ percentNum(arrSum(map_data1,9),totalNum) +'%</div>';
            str += '</div>';
            return str;
        }
        document.getElementById("map-top10").innerHTML = mapTop10(map_data1);
    });
}

function allFun(){
    setMap();//地图
    $(".data-totalTime").text(dataVal.plat_total[0].date);//截止日期

    //总数据
    var plat_total = dataVal.plat_total.sort(getSortFun('asc', "type"));

    //数字动画
    function numAnimate(dom,num,xs){
        // 需要保留的小数位数
        if(!xs && xs != 0){
            xs = 1;
        }
        var decimal_places = xs;
        dom.animateNumber({
            number: parseFloat(num),
            easing: 'easeInQuad',
            numberStep: function(now, tween) {
                var floored_number = parseFloat(now),
                    target = $(tween.elem);
                if (decimal_places > 0) {
                  floored_number = floored_number.toFixed(decimal_places);
                }
                target.text(fmoney(floored_number,decimal_places));
              }
        });
    }

    $(".data-money1").text(numDivision(plat_total[9].Qty,10000));//累计投资金额
    $(".data-money2").text(numDivision(plat_total[0].Qty,10000));//线上投资金额
    $(".data-money3").text(numDivision(plat_total[8].Qty,10000));//线下投资金额
    $(".data-money4").text(numDivision(plat_total[10].Qty,1,0));//智慧投资人

    $(".data-money5").text(numDivision(plat_total[2].Qty,10000));//线上已还本金
    $(".data-money6").text(numDivision(plat_total[6].Qty,10000));//线上已发放收益
    $(".data-money7").text(numDivision(plat_total[11].Qty,10000));//线上未还本金
    $(".data-money8").text(numDivision(plat_total[4].Qty,10000));//线上未发放收益


    //平台7日数据
    $(".seven-time").html("（"+ getBeforeDate(dataVal.plat_total[4].date,6).replace(/-/g,".") + " - " + dataVal.plat_total[4].date.replace(/-/g,".")  + ")");

    var mySwiper = new Swiper ('#page-swipe', {
      direction: 'vertical',
      loop: false,
      onSlideChangeEnd: function(swiper){
          var self = $(".swiper-slide-active");
          var cname = self.attr("class");
          var inx = cname.indexOf("page");
          var nowDom = cname.substr(inx,5);
          if(nowDom == "page9"){
              $("#next-box").hide();
          }else{
              $("#next-box").show();
          }
          switch (nowDom){
              case "page2":
                  numAnimate($(".data-money1"),numDivision(plat_total[9].Qty,10000));
                  setTimeout(function(){numAnimate($(".data-money2"),numDivision(plat_total[0].Qty,10000));},500);
                  setTimeout(function(){numAnimate($(".data-money3"),numDivision(plat_total[8].Qty,10000));},1000);
                  setTimeout(function(){numAnimate($(".data-money4"),numDivision(plat_total[10].Qty,1),0);},1500);
                  //numAnimate($(".data-money2"),numDivision(plat_total[0].Qty,10000));
                  //numAnimate($(".data-money3"),numDivision(plat_total[8].Qty,10000));
                  //numAnimate($(".data-money4"),numDivision(plat_total[10].Qty,1),0);
                  break;
              case "page3":
                  numAnimate($(".data-money5"),numDivision(plat_total[2].Qty,10000));
                  //numAnimate($(".data-money6"),numDivision(plat_total[6].Qty,10000));
                  //numAnimate($(".data-money7"),numDivision(plat_total[11].Qty,10000));
                  //numAnimate($(".data-money8"),numDivision(plat_total[4].Qty,10000));
                  setTimeout(function(){numAnimate($(".data-money6"),numDivision(plat_total[6].Qty,10000));},500);
                  setTimeout(function(){numAnimate($(".data-money7"),numDivision(plat_total[11].Qty,10000));},1000);
                  setTimeout(function(){numAnimate($(".data-money8"),numDivision(plat_total[4].Qty,10000));},1500);

                  break;
              case "page5":
                  numAnimate($(".seven-money1"),numDivision(plat_total[1].Qty,10000),2);
                  numAnimate($(".seven-money2"),numDivision(plat_total[3].Qty,10000),2);
                  numAnimate($(".seven-money3"),numDivision(plat_total[5].Qty,10000),2);
                  numAnimate($(".seven-money4"),numDivision(plat_total[7].Qty,10000),2);
                  break;
          }
      }
    });

    //线上月交易额
    $("div.page4 .page-tab-cont").on("click","div.bar-item",function(){
        var self = $(this),
            page = self.parents("div.swiper-slide");
        var num = self.attr("data-num");
        var month = self.attr("data-month");
        self.addClass("active").siblings("div.bar-item").removeClass("active");
        page.find(".page4-month").text(month);
        page.find(".page4-month-num").text(num+"元");
    });
    //tab
    $("ul.page-tab-nav").on("click","li.nav-item",function(){
        var self = $(this),
            inx = self.index();
        var page4 = self.parents("div.swiper-slide");
        var cont = page4.find("ul.page-tab-cont"),
            contLi = cont.find("li.cont-item").eq(inx),
            barItem = contLi.find("div.bar-item.active");
        self.addClass("active").siblings("li").removeClass("active");
        contLi.addClass("active").siblings("li.cont-item").removeClass("active");
        page4.find(".page4-month").text(barItem.attr('data-month'));
        page4.find(".page4-month-num").text(barItem.attr('data-num')+"元");
    });

    function page4(){
        var yearData = dataVal.year;
        var page4 = $("div.page4");
        var page4Nav = page4.find("ul.page-tab-nav"),
            page4Cont = page4.find("ul.page-tab-cont");
        var navHtml = '',
            contHtml = '',
            contLiHtml = '',
            liHeight = 0,
            aNum = yearData.length;
        var aClass = '',
            liActive = '';
        var contDom = '';

        for(var y=0; y<aNum; y++){
            var tmpYearDate = yearData[y].data;
            contLiHtml = '';
            if(y === (aNum-1)){
                aClass = " active";
            }else{
            }
            navHtml += '<li class="nav-item'+ aClass +'">'+ yearData[y].year +'年</li>';
            contDom = '<li class="cont-item'+ aClass +'">'+
                '<div class="tab-cont-bg"></div><div class="line-unit">单位：千万元</div>'+
                '<div class="line-y">'+
                  '<div class="line-money">50</div>'+
                  '<div class="line-money">40</div>'+
                  '<div class="line-money">30</div>'+
                  '<div class="line-money">20</div>'+
                  '<div class="line-money">10</div>'+
                '</div>'+
                '<div class="line-bar">';
            for(var m=0; m<tmpYearDate.length; m++){
                var liData = tmpYearDate[m];
                var liMonth = parseInt(liData.date.substr(5,2));
                if(m === (tmpYearDate.length-1)){
                    liActive = " active";
                    page4.find(".page4-month").text(liMonth);
                    page4.find(".page4-month-num").text(liData.invest+"元");
                }else{
                   liActive = '';
                }
                liHeight = parseFloat(percentNum(liData.invest.replace(/,/g,''),50*10000000));

                contLiHtml += '<div class="bar-item'+ liActive +'" data-num='+ liData.invest +' data-month='+ liMonth +'>'+
                                '<div style="bottom: '+ (liHeight+3) +'%" class="bar-top">'+
                                  '<div class="bar-top-item"></div>'+
                                  '<div class="bar-top-item"></div>'+
                                '</div>'+
                                '<div class="has-an year-bar"><div style="height:'+ liHeight +'%" class="bar-img"></div></div>'+
                                '<div class="line-month">'+liMonth+'月</div>'+
                              '</div>';
            }
            contDom += contLiHtml + '</div></li>';
            contHtml += contDom;
        }

        page4Cont.html(contHtml);
        page4Nav.html(navHtml);
    }
    page4();


    //性别
    var sex_data = dataVal.sex;
    var sex_man = percentNum(sex_data[2].QTY.replace(/,/g,""),arrSumQTY(sex_data));
    $(".sex-women").text((100-sex_man)+"%");
    $(".sex-man").text(sex_man+"%");
    //年龄
    ;(function(){
        var age_data = dataVal.age;
        var ageDom = $("div.page7 .page-age-item");
        var maxAgeNum = 0,
            totalAge = arrSumQTY(age_data);

        for(var i=0; i<age_data.length; i++){
            age_data[i].QTY = parseFloat(age_data[i].QTY.replace(/,/g,''));
        }
        maxAgeNum = age_data.sort(getSortFun('desc', 'QTY'))[0].QTY;

        var perTotal = percentNum((dataVal.age[5].QTY+dataVal.age[6].QTY),totalAge)+"%",
            perMax = percentNum((dataVal.age[5].QTY+dataVal.age[6].QTY),maxAgeNum);
        ageDom.eq(0).find(".age-tit").text(perTotal).css("bottom",(perMax+3)+"%");
        ageDom.eq(0).find(".age-bar").css("height",perMax+"%");
        for(var j=1; j<ageDom.length; j++){
            perTotal = percentNum(dataVal.age[j-1].QTY,totalAge)+"%";
            perMax = percentNum(dataVal.age[j-1].QTY,maxAgeNum);
            ageDom.eq(j).find(".age-tit").text(perTotal).css("bottom",(perMax+3)+"%");
            ageDom.eq(j).find(".age-bar").css("height",perMax+"%");
        }
    })();

    setTimeout(function(){
      $("div.page-loading").hide();//加载ok
      $("#next-box").show();
    },500);

}






