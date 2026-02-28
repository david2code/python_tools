#!/bin/bash

# 使用nc不停监听一个端口
# 可以使用 ./nc.sh 8001 &
# 在后台运行
while [ true ]
do
  nc -l $1
  echo "done"
done