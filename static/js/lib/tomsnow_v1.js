// TOM'S EXCELLENT JAVASCRIPT SNOW
// Unobtrusive and customisable javascript snow for web pages using no images
//
// tomsnow_v1.js
// http://www.aurochs.org/tomsnow/tomsnow_v1.js
//
// By Thomas Meehan,
// screenSize function adapted from alertSize function by Mark "Tarquin" Wilton-Jones at http://www.howtocreate.co.uk/tutorials/javascript/browserwindow
// 11 December 2008

// INSTALLATION
//Copy this file into a directory on your own web server. To add it to pages, add the following to the head of each page, changing the URL as appropriate and removing the double-slash comments:
//
// <script type="text/javascript" src="http://www.yourdomain.com/path/tomsnow_v1.js"></script>
// <script type="text/javascript">
// function init () {
//   snow();
// }
// window.onload=init;
// <script>

// CUSTOMISATION
// The settings that can be customised, such as number of flakes and speed, can be found in the section between asterisks below. Where formulas have been used, alternatively lines with simple numbers are also given commented and can be uncommented and altered as necessary. 



// Get page dimensions and information.
	var pageWidthHeight=screenSize();
	var pageWidth=pageWidthHeight[0]*.95;
	var pageHeight=pageWidthHeight[1]*.95;

//************************************************************************************************
// This section includes seetings that can be customised, such as number of flakes and speed. Where formulas have been used, alternatively lines with simple numbers are also given commented and can be uncommented and altered as necessary. 

// snowflake numbers and density, and speed settings
	var max_snowflakes=Math.round((pageWidth*pageHeight)/10000); // maximum number of snowflakes: this is calculated based on the screen size. Can be changed to a different formula or a simple number as in the following commented line:
	//var max_snowflakes=150;
	var speed=1; // pixels per cycle of smallest snowflake. Larger flakes fall faster.
	var interval=75 // millisecond between cycle
	var density=2/(pageHeight/max_snowflakes); // Chance of new snowflake on each iteration: this is calculated based on the screen size. Can be changed to a different formula or a simple number as in the following commented line:
	//var density=.16; // 
	var snowflake_crystal="*"; // Character used to draw the snowflake
	var snow_font="time new roman"; // font used to draw the snowflake
	var max_snowsize=130; // Maximum size of snowflakes in pixels - not points!
	var min_snowsize=15;  // Minimum size of snowflakes in pixels - not points!
	var snowcolour="#ddeeee"; // colour of snowflakes: default is slightly blue so they show up against white pages. For white, uncomment next line:
	// var snowcolour="#ffffff";
	var max_snowsize_for_calc=max_snowsize-min_snowsize;

//************************************************************************************************

// Create container div to hold all the snowflakes
	var bodytag=document.getElementsByTagName("body");
	container=document.createElement("div");

// set snowflake arrays
	var snowheight=new Array ();
	var snowwidth=new Array ();
	var snowflake=new Array ();
	var snowsize=new Array ();

function snow () { // Start snow by setting up container div, creating first snowflake, and calling snowfall
	bodytag[0].appendChild(container);
	container.style.position="absolute";
	container.style.top="0px";
	container.style.height=pageHeight;
	container.style.zIndex="100";
	create_snowflake(0);
	setTimeout(snowfall,interval);
}

function create_snowflake (x) {
	
	snowflake[x]=document.createElement("p"); // create p tag and attach snowflake_crystal character to it
	crystal=document.createTextNode(snowflake_crystal);
	snowflake[x].appendChild(crystal);
	snowwidth[x]=Math.random()*pageWidth; // set random horizontal position of snowflake
	snowflake[x].style.position="absolute";
	snowflake[x].style.left=snowwidth[x]+"px";
	snowsize[x]=min_snowsize+Math.round((Math.random()*max_snowsize_for_calc)); // set random size of snowflake
	snowflake[x].style.fontSize=snowsize[x]+"px";
	snowheight[x]=0-snowsize[x]; // set starting position of snowflake off top of screen, further up for larger flakes
	snowflake[x].style.top=snowheight[x]+"px";
	snowflake[x].style.color=snowcolour; // various style declarations for the new snowflake
	snowflake[x].style.fontFamily=snow_font;
	snowflake[x].style.padding="0px";
	snowflake[x].style.border="0px";
	snowflake[x].style.margin="0px";
	snowflake[x].style.opacity=".7"; // make snowflakes slightly see-through for Mozilla
	snowflake[x].style.filter="alpha(opacity=70)"; // make snowflakes slightly see-through for IE
	container.appendChild(snowflake[x]); // attach finished snowflake to container div
}

function snowfall () { // Regulates random sideways drift, rate of snowfall, detects hitting the ground, and calls itself to continue
	for (y=0; y<snowflake.length; y++) {
		drift=Math.random(); // Determine random horizontal drift
		if (drift>.1) {snowwidth[y]+=1};
		if (drift<.9) {snowwidth[y]-=1};
		if (snowwidth[y]<1) {snowwidth[y]=pageWidth-1} // wrap it round over the edges if necessary
		if (snowwidth[y]>pageWidth-1) {snowwidth[y]=1}
		snowflake[y].style.left=snowwidth[y]+"px";
		var dropspeed=Math.round(snowsize[y]*speed)/16;  // Determine speed of drop, based on size of flake
		if (dropspeed<1) {dropspeed=1}
		snowheight[y]+=dropspeed;
		snowflake[y].style.top=snowheight[y]+"px"; // move snowflake down
		if (snowheight[y]+((snowsize[y]*speed)/16)>pageHeight-snowsize[y]) { // Check for hitting the ground and reset random settings
			snowwidth[y]=Math.random()*pageWidth; // get snowflake off the page until other settings in place to stop it seeming to explode
			snowflake[y].style.top=0-(2*snowsize[y])+"px";
			snowsize[y]=min_snowsize+  Math.round((Math.random()*max_snowsize_for_calc));
			snowflake[y].style.fontSize=snowsize[y]+"px";
			snowheight[y]=0-snowsize[y];
		}
	}
	if (snowflake.length<max_snowflakes && Math.random()<density) { // randomly create new snowflakes if not at maximum
		create_snowflake(snowflake.length);
	}
	setTimeout (snowfall,interval); // continue snowfall after interval
}

function screenSize() { // adapted from alertSize function by Mark "Tarquin" Wilton-Jones at http://www.howtocreate.co.uk/tutorials/javascript/browserwindow
  var myWidth = 0, myHeight = 0;
  if( typeof( window.innerWidth ) == 'number' ) {
    //Non-IE
    myWidth = window.innerWidth;
    myHeight = window.innerHeight;
  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    //IE 6+ in 'standards compliant mode'
    myWidth = document.documentElement.clientWidth;
    myHeight = document.documentElement.clientHeight;
  } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
    //IE 4 compatible
    myWidth = document.body.clientWidth;
    myHeight = document.body.clientHeight;
  }
   return [myWidth,myHeight];
}
