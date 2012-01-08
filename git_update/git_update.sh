#!/bin/sh

cd ~/repository/sw/xilinx_git
for dir in *
do
  cd $dir
  echo $PWD
  git pull
  cd ..
done
cd


