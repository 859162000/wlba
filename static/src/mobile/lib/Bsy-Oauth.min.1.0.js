/**
 * 比搜益【H5/WAP】网页授权回调函数使用说明：
 * --------------------------------------------------------------------------------------------------------------------
 * 1、乙方使用说明, 在注册授权/登录授权的结果页面/流程中回调JS函数：BSY.Oauth(授权json串);
 * JSON数据响应格式举例说明【数据类型不能错误,否则校验不过】：
 * {
 * 	 "pcode" : "BSY-BIZ-10001", 				// 【字符串类型】, 甲方分配乙方平台编码
 *   "token" : "jkyls86kh23dl2h32llj3hk23h", 	// 【字符串类型】, 授权指令
 *   "stime" : 192382087827322, 				// 【长整型】, 授权开始时间
 *   "etime" : 192382089212345, 				// 【长整型】, 授权截止时间:(etime-stime)=t,[t=0表示永久授权,t<0表示失效,t>0表示剩余过期时间]
 *   "status" : 1 								// 【整型】, 授权状态:0表示失败, 1表示成功
 * }
 * 2、甲方使用说明, APP转换结果数据举例说明：
 * 成功：数据格式正确/授权正确:{'pcode':'甲方分配乙方平台编码','token':'授权指令','stime':19238208782732,'etime':192382089212345,'status':1}
 * 失败：数据格式错误/授权错误:{'pcode':'','token':'','stime':-1,'etime':-1,'status':0}
 * --------------------------------------------------------------------------------------------------------------------
 */
BSY={Review:function(b){var a=0,e="";for(var d in b){var c=b[d];if(d==="pcode"||d==="token"){if(typeof c==="string"){e+="'"+d+"':'"+c+"',";(++a)}continue}if(d==="stime"||d==="etime"){if(typeof c==="number"){e+="'"+d+"':"+c+",";(++a)}continue}if(d==="status"){if(c===0||c===1){e+="'"+d+"':"+c+",";(++a)}continue}}if(a===5){return"{"+e.substring(0,e.length-1)+"}"}else{return"Invalid"}},Format:function(d,a){var b=d==null?"{'pcode':'','token':'','stime':-1,'etime':-1,'status':0}":d;if(a==="ios"){return b.replace(/\"/g,"\'")}else{if(a==="android"){return b.replace(/\'/g,'\"')}else{throw new Error("Format")}}},Oauth:function(g){var b="",a=true;try{b=BSYAPP.jsVersion();b+=""}catch(c){}finally{setTimeout(function(){if((typeof b==="undefined")||b==null||b===""){a=false;alert("BSY:获取版本错误[ "+c.message+" ]");return}},500);if(!a){return}}try{if((typeof g==="undefined")||g==null||g===""){if(b==="ios"){BSYAPP.jsCallackFailure(BSY.Format(null,b));return}if(b==="android"){BSYAPP.jsCallackFailure(BSY.Format(null,b));return}else{alert("BSY:授权失败[ 版本不支持 ]");return}}}catch(c){alert("BSY:校验数据错误[ "+c.message+" ]");return}var f=null;try{if(typeof g==="object"){f=BSY.Review(g)}else{if(typeof g==="string"){f=BSY.Review((new Function("","return "+BSY.Format(g,b))))}else{throw new Error("Json error")}}}catch(c){try{BSYAPP.jsCallackException(c.message)}catch(c){alert("BSY:校验格式错误[ "+c.message+" ]")}return}if(f==null||f==="Invalid"){try{BSYAPP.jsCallackFailure(BSY.Format(null,b))}catch(c){alert("BSY:授权失败[ 无效数据错误: "+c.message+" ]")}}else{try{BSYAPP.jsCallackSuccess(BSY.Format(f,b))}catch(c){alert("BSY:授权失败[ 有效数据错误: "+c.message+" ]")}}}};
