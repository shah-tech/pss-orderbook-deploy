#!/bin/bash
#
#
# this script can be used to generate pipeline scripts for Jenkins based on template
# usage : ./set_team_pipeline <COHORT> <NUMBEROFTEAM>
#
#
#


COHORT=$1
NUMBEROFTEAM=$2

if [[ $# -lt 2 ]]
then
	echo "please provide at least 2 args"
	echo "./set_team_pipeline <COHORT> <NUMBEROFTEAM>"
	exit 1
fi
if ! [[ $NUMBEROFTEAM =~ ^[0-9]+$ ]]
then
	echo "incorrect format for numberofteam, expecting a number"
	exit 1
fi

# Updating Image Build Pipeline

sed -e "s/<COHORT>/${COHORT}/g" -e "s/<NUMBEROFTEAM>/${NUMBEROFTEAM}/g" template/pipeline_multi_team_build.tmplt > pipeline_multi_team_build

# Updating Promote Pipeline

sed -e "s/<COHORT>/${COHORT}/g" -e "s/<NUMBEROFTEAM>/${NUMBEROFTEAM}/g" template/pipeline_promote_multi_team.tmplt > pipeline_promote_multi_team

# git instruction

echo "Don't forget to push your changes to git!"

