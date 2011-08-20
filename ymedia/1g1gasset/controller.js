var defaultDisplayText = document.getElementById("displayText_1g1g").innerHTML; //默认显示的文字
document.write('<div style="width:0;height:0;position:absolute;top:0;left:0;">');
document.write('<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0" id="commander1g1g" width="100%" height="100%">');	
document.write('<param name="movie" value="/ymedia/1g1gasset/commander.swf"/>');	
document.write('<param name="allowScriptAccess" value ="always" />');	
document.write('<EMBED src="/ymedia/1g1gasset/commander.swf" allowScriptAccess="always" width="100%" height="100%" name="commander1g1g"  type="application/x-shockwave-flash" PLUGINSPAGE="http://www.macromedia.com/go/getflashplayer" />');	
document.write('</object></div>');
var playPauseBtn_1g1g = document.getElementById("playPauseBtn_1g1g");
var nextBtn_1g1g = document.getElementById("nextBtn_1g1g");
var displayText_1g1g = document.getElementById("displayText_1g1g");
var controller_1g1g = document.getElementById("controller_1g1g");
var commander_1g1g = get1gCommander();
var playerState; 

controllerInit();
function controllerInit()
{
	controllerReset();
	playPauseBtn_1g1g.onclick =onPlayPauseBtnClick;	
	playPauseBtn_1g1g.onmouseover=onPlayPauseBtnMouseOver;
	playPauseBtn_1g1g.onmouseout =onPlayPauseBtnMouseOut;
	nextBtn_1g1g.onclick=onNextBtnClick;
	nextBtn_1g1g.onmouseover=onNextBtnMouseOver;
	nextBtn_1g1g.onmouseout =onNextBtnMouseOut;
	controller_1g1g.onclick = onControllerClick;
}


function get1gCommander()
{
	if (navigator.appName.indexOf("Microsoft") != -1) {
		return window["commander1g1g"];
	} else {
		return document["commander1g1g"];
	}
}


function controllerReset()
{
	displayText_1g1g.innerHTML = defaultDisplayText;
	playPauseBtn_1g1g.style.backgroundPosition = "0px 0px";
	controller_1g1g.style.cursor = "pointer";
	playerState = "stop";		
}
function onControllerClick()
{
	if(!commander_1g1g.command("is1g1gPlayerOpen"))
	{
		open1g1gPlayer();
	}			
}			

function playerEventDispatcher(type, body)  //相应播放器返回事件，做出相应的调整
{
	
	if(type == "connect")
	{					
		commander_1g1g.command("getStatus", "playerState");
		commander_1g1g.command("getStatus", "display");
		controller_1g1g.style.cursor = "default";
	}
	else if(type == "display")
	{
		displayText_1g1g.innerHTML = body.text;
	}
	else if(type == "playerState")
	{	
		playerState = body.state;
		if (playerState == "stop" || playerState == "paused") 
		{
			playPauseBtn_1g1g.style.backgroundPosition = "0px 0px";
			commander_1g1g.command("getStatus", "currentSongInfo");
		}
		else
		{
			playPauseBtn_1g1g.style.backgroundPosition = "0px -32px";
		}
	}
	else if(type == "disconnect")
	{
		controllerReset();
	}
} 
function open1g1gPlayer()
{
	window.open (playerUrl,'newwindow','height=460,width=360, toolbar=no,menubar=no,scrollbars=no,resizable=yes,location=no,status=no') 
}

function onPlayPauseBtnClick()
{
	if(commander_1g1g.command("is1g1gPlayerOpen"))
	{
		commander_1g1g.command("playPause");
	}
	else
	{
		open1g1gPlayer();
	}
}
function onPlayPauseBtnMouseOver()
{
	if (playerState == "stop" || playerState == "paused") 
	{
		playPauseBtn_1g1g.style.backgroundPosition = "0 -16px"; 
	}
	else
	{
		playPauseBtn_1g1g.style.backgroundPosition = "0 -48px"
	}
	
}
function onPlayPauseBtnMouseOut()
{
	if (playerState == "stop" || playerState == "paused") 
	{
		playPauseBtn_1g1g.style.backgroundPosition = "0px 0px"
	}
	else
	{
		playPauseBtn_1g1g.style.backgroundPosition = "0px -32px"
	}
}
function onNextBtnClick()
{
	if(commander_1g1g.command("is1g1gPlayerOpen"))
	{
		commander_1g1g.command("next");
	}
	else
	{
		open1g1gPlayer();
	}
}
function onNextBtnMouseOver()
{
	nextBtn_1g1g.style.backgroundPosition='0px -80px'
	
}
function onNextBtnMouseOut()
{
	nextBtn_1g1g.style.backgroundPosition='0px -64px'
}
