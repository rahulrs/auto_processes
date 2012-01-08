#!/bin/sh

touch synthesis_run.log

echo "Start time" > synthesis_run.log
date >> synthesis_run.log

make init_bram

echo "End time" >> synthesis_run.log
date >> synthesis_run.log


