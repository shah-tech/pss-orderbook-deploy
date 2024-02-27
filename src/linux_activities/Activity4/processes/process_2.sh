#!/bin/sh


LOG=log/process_2.log
rm $LOG
i=0
while [ $i -lt '101' ]
do
echo "process is running $i % complete" >> $LOG
sleep 5
i=$(($i+1))
done

