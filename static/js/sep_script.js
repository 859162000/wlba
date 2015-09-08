function randomnum(smin, smax) {// 获取2个值之间的随机数
	var Range = smax - smin;
	var Rand = Math.random();
	return (smin + Math.round(Rand * Range));
}

function runzp(index) {
	var data = '[{"id":1,"prize":"1月爱奇艺会员","v":1.0},{"id":2,"prize":"扣电影50元代金券","v":1.0},{"id":3,"prize":"200元现金红包","v":2.0},{"id":4,"prize":"150元现金红包","v":3.0},{"id":5,"prize":"100元现金红包","v":4.0}]';// 奖项json
	var obj = eval('(' + data + ')');
	var result = randomnum(1, 100);
	var line = 0;
	var temp = 0;
	var returnobj = "1";
	var index = index;

	var angle = 330;
	var message = "";
	var myreturn = new Object;
	if (returnobj != "0") {// 有奖
		message = "恭喜中奖了";
		var angle0 = [ 210, 250 ];
		var angle1 = [ 255, 292 ];
		var angle2 = [ 117, 160 ];
        var angle3 = [ 298, 335 ];
		var angle4 = [ 23, 65 ];
		switch (index) {
		  case 0:// 一等奖
			var r0 = randomnum(angle0[0], angle0[1]);
			angle = r0;
			break;
		  case 1:// 二等奖
			var r1 = randomnum(angle1[0], angle1[1]);
			angle = r1;
			break;
		  case 2:// 三等奖
			var r2 = randomnum(angle2[0], angle2[1]);
			angle = r2;
			break;
          case 3:// 四等奖
			var r3 = randomnum(angle3[0], angle3[1]);
			angle = r3;
			break;
		  case 4:// 4等奖
			var r4 = randomnum(angle4[0], angle4[1]);
			angle = r4;
			break;
		}
		myreturn.prize = obj[index].prize;
	} else {// 没有
		message = "再接再厉";
		var angle5 = [ -22, 19 ];
		var angle6 = [ 165, 205 ];
		var r = randomnum(5, 6);
		var angle;
		switch (r) {
		case 5:
			var r5 = randomnum(angle5[0], angle5[1]);
			angle = r5;
			break;
		case 6:
			var r6 = randomnum(angle6[0], angle6[1]);
			angle = r6;
			break;
		}
		myreturn.prize = "继续努力!";

	}
	myreturn.angle = angle;
	myreturn.message = message;
	return myreturn;
}