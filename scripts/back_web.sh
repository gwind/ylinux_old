#!/bin/sh

TIMESTR=$1
if [ -z "$TIMESTR" ]; then
    echo 'YOU MUST SPECIFY THE $1 ARG'
    exit 1
fi

PASSWORD=$2
if [ -z "$PASSWORD" ]; then
    echo 'YOU MUST SPECIFY THE $2 for PASSWORD'
    exit 1
fi


D_BACKUP="/www/lijian.gnu/ylinux_org/backups/"
D_YLINUX="ylinux-${TIMESTR}"

D_YDATA="/www/lijian.gnu/ylinux_org/htdocs/ylinux/ymedia/ydata/"

# 创建目录存放备份
cd $D_BACKUP
[ -d $D_YLINUX ] || mkdir $D_YLINUX

# 备份 MySQL 数据库
cd ${D_BACKUP}/${D_YLINUX}
/usr/local/bin/mysqldump -uylinux -p"$PASSWORD" ylinux > ylinux.sql

# 备份 YLinux 的 Topics
cd ${D_YDATA}
find topics/ -name \*.src | cpio -o | bzip2 > ${D_BACKUP}/${D_YLINUX}/topic.cpio.bz2

# 打包
cd ${D_BACKUP}
tar cjf ${D_YLINUX}.tar.bz2 ${D_YLINUX}
rm -rf ${D_YLINUX}

echo "Backup success: ${D_BACKUP}/${D_YLINUX}.tar.bz2"
exit 0