#!/bin/sh
# SVN update runs automatically at 7 am everyday
# Then a mail is sent out to rahuluncc@gmail.com (done by 'ray')

datestamp=`date` 
echo
echo "Repository Sync started at" $datestamp > ~/repo_update.log
echo
echo "==================================================" >> ~/repo_update.log

# Update Lab SVN
echo "svn up ~/svn/rcc" >> ~/repo_update.log
svn up ~/svn/rcc >> ~/repo_update.log
echo "==================================================" >> ~/repo_update.log
echo "svn up ~/svn/reports" >> ~/repo_update.log
svn up ~/svn/reports >> ~/repo_update.log
echo "==================================================" >> ~/repo_update.log
echo "svn up ~/svn/proposals" >> ~/repo_update.log
svn up ~/svn/proposals >> ~/repo_update.log
echo "==================================================" >> ~/repo_update.log
cd

# Update Opencores - Amber 
echo "svn up /home/rsharm14/storage/amber_opencores/" >> ~/repo_update.log
svn up /home/rsharm14/storage/amber_opencores/ >> ~/repo_update.log
echo "==================================================" >> ~/repo_update.log
# Update Opencores - OpenRISC
echo "svn up /home/rsharm14/storage/openrisc_opencores/" >> ~/repo_update.log
svn up /home/rsharm14/storage/openrisc_opencores/ >> ~/repo_update.log
echo "==================================================" >> ~/repo_update.log

# Update Xilinx GIT repository
cd ~/repository/sw/xilinx_git
for dir in *
do
  cd $dir
  echo $PWD >> ~/repo_update.log
  git pull >> ~/repo_update.log
  cd ..
  echo "==================================================" >> ~/repo_update.log
done
cd
echo
datestamp=`date` 
echo "Repository Sync completed at" $datestamp >> ~/repo_update.log
echo 

# A Second cron job on 'ray' mails the file daily at 8 am to rahuluncc@gmail.com
# A Third cron job on 'ray' deletes the log file at 9 am

