﻿function randomnum(smin, smax) {// 获取2个值之间的随机数
	var Range = smax - smin;
	var Rand = Math.random();
	return (smin + Math.round(Rand * Range));
}

function runzp(index) {
	var data = '[{"id":1,"prize":"1000元","v":1.0},{"id":2,"prize":"500元","v":2.0},{"id":3,"prize":"200元","v":3.0},{"id":4,"prize":"50元","v":4.0}]';// 奖项json
	var obj = eval('(' + data + ')');
	var returnobj = "1";
	var index = index;

	var angle = 330;
	var message = "";
	var myreturn = new Object;
	if (returnobj != "0") {// 有奖
		message = "恭喜中奖了";
		var angle0 = [ 212, 245 ];
		var angle1 = [ 120, 160 ];
		var angle2 = [ 25, 65 ];
        var angle3 = [ 298, 330 ];
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
		}
		myreturn.prize = obj[index].prize;
	}
	myreturn.angle = angle;
	myreturn.message = message;
	return myreturn;
}