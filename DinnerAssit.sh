#!/bin/sh 
#input: sh run.sh hour minute
#example: sh run.sh 11 30 
# sh run.sh

PDIR=dist
#read config
username=`sed '/^用户名=/!d;s/.*=//' config.txt`
ordertime=`sed '/^预定时间=/!d;s/.*=//' config.txt`
echo '[username]\nusername='$username'\n[ordertime]\nordertime = '$ordertime > ./$PDIR/config.txt
cat  本周菜单.txt  > ./$PDIR/本周菜单.txt

#parse ordertime
minute=`echo $ordertime | cut -d ':' -f 2`
hour=`echo $ordertime | cut -d ':' -f 1`
#if then fi switch line
if [ -n "$2" ]; then 
	minute=$2
fi
if [ -n "$1" ]; then 
	hour=$1 
fi
if [ -z "$hour" ]; then 
	hour="11"
fi
if [ -z "$minute" ]; then 
	minute="30"
fi

#generate the plist config
runfile=88888888
curDir=`pwd`
startfile=~/Library/LaunchAgents/com.order.dinner.launchctl.plist
rm ~/Library/LaunchAgents/com.order.dinner.launchctl.plist
config='<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n
<plist version="1.0">\n
<dict>\n
<key>Label</key>\n
<string>com.order.dinner.launchctl.plist</string>\n
<key>ProgramArguments</key>\n
<array>\n
<string>'$curDir'/'$runfile'.sh</string>\n
 </array>\n
 <key>StartCalendarInterval</key>\n
 <dict>\n
 <key>Minute</key>\n
 <integer>'
config=$config$minute
config=$config'</integer>\n
  <key>Hour</key>\n
  <integer>\n'
config=$config$hour
config=$config'</integer>\n
   </dict>\n
   <key>StandardOutPath</key>\n
   <string>'
   config=$config$curDir'/order_dinner.log</string>\n
   <key>StandardErrorPath</key>\n
   <string>'$curDir'/order_dinner.err</string>\n
   </dict>\n
   </plist>' 
echo $config > com.order.dinner.launchctl.plist
cp com.order.dinner.launchctl.plist ~/Library/LaunchAgents/com.order.dinner.launchctl.plist  

#start launchctl
launchctl unload $startfile
launchctl load $startfile
launchctl start $startfile 

#./order_dinner/order_dinner
if [ -f "./order_dinner/菜单.txt" ]; then
	mv ./$PDIR/菜单.txt $curDir
fi

#generate the run comman 
cp 本周菜单.txt ./$PDIR/
echo $curDir'/'$PDIR'/order_dinner' > $runfile'.sh'
#add the perms
chmod 777 $runfile'.sh'
