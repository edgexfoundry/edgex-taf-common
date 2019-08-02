#!/bin/bash

########################################################
## Copyright (c) 2019 Intel Corporation
## SPDX-License-Identifier: Apache-2.0
## 
########################################################

## The script called as TAF-Manager, aims to provide the service for TAF such as,
## TAF execution, orchestration and reporting.
##

## Command Line arguments
##
vPROJ_CONF=$1
if [[ ! -f ${vPROJ_CONF} ]]; then
	echo "Missing project configuration! Terminating the execution"
fi

## Function to extract the value from configuration file
##
function fnExtractConf {
        temp=("`cat ${vPROJ_CONF} | grep -i ^$1= | sed "s/\$1=//"`");
        echo ${temp}
}

## Variable definitions
##
vBUILD_NUMBER=$(fnExtractConf JK_BUILD_NUMBER)
vGIT_REPO=$(fnExtractConf GIT_REPO_NAME)
vREPO_LOCATION=$(fnExtractConf JK_CHECKOUT_DIR)

vSCRIPT_LOCATION="${vREPO_LOCATION}/TAF-Common/TAF-Manager/trigger"
vCFG_TEMPLATE_LOCATION="${vREPO_LOCATION}/TAF/config"
vTEST_SCENARIO_LOCATION="${vREPO_LOCATION}/TAF/testScenarios"
vMAIL_TEXT="${vSCRIPT_LOCATION}/mailText.html"
vMAIL_TEXT_TEMPLATE="${vSCRIPT_LOCATION}/mailText_template.html"
vUC_NAMES=(`cat ${vPROJ_CONF} | grep -i ^UC_NAMES= |  sed 's/UC_NAMES=//' | sed 's/:[0-9]*//g' | sed 's/\://g'`);
vUC_ITERATIONS=(`cat ${vPROJ_CONF} | grep -i ^UC_NAMES= |  sed 's/UC_NAMES=//' | sed 's/\_//g' | sed 's/[A-Za-z]*//g' | sed 's/[0-9]://g' | sed 's/\://g'`);
vPROFILE_NAMES=(`cat ${vPROJ_CONF} | grep -i ^PROFILE_NAMES= |  sed 's/PROFILE_NAMES=//' | sed 's/:[0-9]*//g' | sed 's/\://g'`);
vROBOT_VARIABLE_1="iterations"
vROBOT_VARIABLE_2="testcase_cfg"
vROBOT_TAGS=$(fnExtractConf ROBOT_TAG)
echo TAG: ${vROBOT_TAGS}
if [[ ${vROBOT_TAGS} != "" ]]; then
	vROBOT_TAGS_OPT="-i ${vROBOT_TAGS}"
else
	vROBOT_TAGS_OPT=""
fi

vROBOT_CFG_FILER=$(fnExtractConf ROBOT_CFG_FILTER)
vROBOT_STOP_ONFAIL=$(fnExtractConf ROBOT_STOP_ONFAIL)
vROBOT_RETRY_ONFAIL=$(fnExtractConf ROBOT_RETRY_ONFAIL)
vROBOT_RETRY_COUNT=$(fnExtractConf ROBOT_RETRY_COUNT)
vROBOT_PASS_COUNT=0
vROBOT_FAIL_COUNT=0
vTC_TEST_DELAY=$(fnExtractConf TC_TEST_DELAY)
tFlag=false

vProfileDir="${vREPO_LOCATION}/TAF/config/profiles"
vTextReport="${vSCRIPT_LOCATION}/TextReport.txt"
declare -A vResultArray;
retryRet=0

vDISABLE_PROXY=$(fnExtractConf DISABLE_PROXY)

if [[ ${vDISABLE_PROXY} == "Yes" ]];then
	unset HTTP_PROXY
	unset HTTPS_PROXY
	unset http_proxy
	unset https_proxy
	env | grep HTTP
	env | grep http
fi


## Display Settings section
##
vDISPLAY_ENABLED=$(fnExtractConf DISPLAY_ENABLED)

if [[ ${vDISPLAY_ENABLED} == "Yes" ]];then
	export DISPLAY=:0
	export $(dbus-launch)
	export NSS_USE_SHARED_DB=ENABLED
fi



## Report Related section starts
##

# LINUX PATH
vARTIFATS_BY_DATE="${vBUILD_NUMBER}"
vTEMP_ARTIFACT_LOCATION="../testArtifacts/${vARTIFATS_BY_DATE}"


## Function definition to place the reports/logs to the staging area
##
function fnPlaceReports {
	echo "fnPlaceReports:  PWD"
	cd ${vTEST_SCENARIO_LOCATION}
	mkdir -v ${vTEMP_ARTIFACT_LOCATION}
	if [[ -d ${vTEMP_ARTIFACT_LOCATION} ]]; then
		echo "fnPlaceReports: Report and Log copy has started..."
		for tArr in "${vUC_NAMES[@]}"
		do
			#mkdir -v ${vTEMP_ARTIFACT_LOCATION}/${tArr}
			echo "fnPlaceReports: UC NAME: ${tArr}"

			cp -r -v ../testArtifacts/reports/${tArr} ${vTEMP_ARTIFACT_LOCATION}/.
			cp -v ../testArtifacts/logs/${tArr}*.log ${vTEMP_ARTIFACT_LOCATION}/${tArr}/.

			files=$(ls ../testArtifacts/reports/${tArr}*png 2> /dev/null | wc -l)
			if [ "$files" != "0" ]; then
				cp -v ../testArtifacts/reports/${tArr}*.png ${vTEMP_ARTIFACT_LOCATION}/${tArr}/.
			fi

			jsonFiles=$(ls ../testArtifacts/reports/${tArr}*json 2> /dev/null | wc -l)
			if [ "$jsonFiles" != "0" ]; then
				cp -v ../testArtifacts/reports/${tArr}*.json ${vTEMP_ARTIFACT_LOCATION}/${tArr}/.
			fi
		done
	else
		echo "fnCopyReport: Can not read Report folder ${vTEMP_ARTIFACT_LOCATION} !!!"
	fi
}

## Function definition to format the mail/slack content
## TBD: This function to redefined as per the Nexus repo usage
##
function fnFormatText {
	echo "In fnFormatText"
	cp -v ${vMAIL_TEXT_TEMPLATE} ${vMAIL_TEXT}

	for tArr in "${vUC_NAMES[@]}"
	do
		echo -e "<p>" >> ${vMAIL_TEXT}
		for tProfileName in "${vPROFILE_NAMES[@]}"
		do
			pwd
			echo "tProfileName: ${tProfileName}"

			## Fetch the Robot files list under UC
			tTS=${vTEST_SCENARIO_LOCATION}/${tArr}/*.robot

			## Fetch the cfg list for the given Robot File
			for tRobot in $tTS
			do
				tmp=$(basename $tRobot)
				tRobotName=${tmp%.*}

				# If config folder is missing, then look for default cfg
				if [[ ! -d ${vTEST_SCENARIO_LOCATION}/${tArr}/${tRobotName} ]]; then
					echo "Config folder ${tRobotName} is not present, looking for default configurations"
					tTSCfg=default.cfg
				else
					vTestConfFilter=${vTEST_SCENARIO_LOCATION}/${tArr}/${tRobotName}/${vROBOT_CFG_FILER}
					if [[ -s ${vTestConfFilter} ]]; then
						tempcfg=(`cat ${vTestConfFilter} | grep -i ^CFG= |  sed 's/CFG=//' | sed 's/:[0-9]*//g' | sed 's/\://g'`);
						tTSCfg=${tempcfg[@]}
						echo "fnFormatText: Picking filtered cfg list: " ${tTSCfg}
					else
						tTSCfg=${vTEST_SCENARIO_LOCATION}/${tArr}/${tRobotName}/*.cfg
					fi
				fi

				for tCfg in ${tTSCfg}
				do
					tmp=$(basename $tCfg)
					tCfgName=${tmp%.*}
					fnPrepareText ${tProfileName} ${tArr} ${tRobotName} ${tCfgName}
				done
			done
		done
		# log
		if [[ -s  ${vTEMP_ARTIFACT_LOCATION}/${tArr}/${tArr}.log ]]; then
			echo "fnPrepareText: Updating mail format for ${tTestExec}.log "
			echo -e "</p>" >> ${vMAIL_TEXT}
		else
			echo "fnPrepareText: ${tTestExec}.log is not present, updating the mailformat"
		fi
	done

	# Test Count Report
	totalCount=`echo $(( ${vROBOT_PASS_COUNT}+${vROBOT_FAIL_COUNT} ))`
	percentage=`printf "%.2f\n" $(echo "($vROBOT_PASS_COUNT / $totalCount) * 100" | bc -l )`
	echo "Total Testcase Executed: ${totalCount}"
	echo "Test-PassCount: ${vROBOT_PASS_COUNT}"
	echo "Test-FailCount: ${vROBOT_FAIL_COUNT}"
	echo "Test-PassPercentage: ${percentage}"

	sed -i "s/Total-TestExecution/Total-TestExecution:  ${totalCount}/" ${vMAIL_TEXT}
	sed -i "s/Test-PassCount/Test-PassCount:  ${vROBOT_PASS_COUNT}/" ${vMAIL_TEXT}
	sed -i "s/Test-FailCount/Test-FailCount:  ${vROBOT_FAIL_COUNT}/" ${vMAIL_TEXT}
	sed -i "s/Test-PassPercentage/Test-PassPercentage:  ${percentage}/" ${vMAIL_TEXT}

	# Footer text
	echo -e "<p>       Note: This is an auto generated mail. Please do not reply </P>" >> ${vMAIL_TEXT}
	echo -e "<p>"
	echo -e "Regards,<br>" >> ${vMAIL_TEXT}
	echo -e "Automation Admin" >> ${vMAIL_TEXT}
	echo -e "</p>" >> ${vMAIL_TEXT}

	## Copy of mail text
	cp -v ${vMAIL_TEXT} ${vTEMP_ARTIFACT_LOCATION}/.

	## Copy Text Report to Artifactory Package
	cp -v ${vTextReport} ${vTEMP_ARTIFACT_LOCATION}/.
}

## Function definition called from fnPlaceReports to prepare the text body
## TBD: This function to redefined as per the Nexus repo usage
##
function fnPrepareText {
	tProfileName=$1
	tArr=$2
	tRobotName=$3
	tCfgName=$4

	tTestExecText=${tArr}-${tRobotName}-${tCfgName}-${tProfileName}
	tTestExec=${tRobotName}-${tCfgName}-${tProfileName}

	echo "fnPrepareText: UC Execution:  ${tTestExec}"
	tResult=${vResultArray["${tTestExec}"]}

	echo "fnPrepareText: UC ${tArr} Status: [ ${tResult} ]"

	if [[ ${tResult} == "Pass" ]]; then
		resultColor="green"
	else
	        resultColor="red"
	fi

	#report
	if [[ -s ${vTEMP_ARTIFACT_LOCATION}/${tArr}/${tTestExec}.html ]]; then
		echo "fnPrepareText: Mail content preparation for ${tTestExecText}"
		echo -e "${tTestExecText}:${tResult}" >> ${vTextReport}
	else
		echo "fnPrepareText: No report for ${tTestExec}"
	fi

	# XML
	if [[ -s ${vTEMP_ARTIFACT_LOCATION}/${tArr}/${tTestExec}.xml ]]; then
		echo "fnPrepareText: XML Parsing for TC of ${tTestExec}"
		tc=`grep "kw name=\"Test" ${vTEMP_ARTIFACT_LOCATION}/${tArr}/${tTestExec}.xml | wc -l`
		sed -i s/TC_${tArr}/$tc/g \
			${vMAIL_TEXT}
	else
		echo "fnPrepareText: No xml found for ${tTestExec}"
		sed -i s/TC_${tArr}/"NA"/g ${vMAIL_TEXT}
	fi
}

## Function definition to prepare the robot execution
##
function fnTaskExecuteRobot {
	tUCArg=$1
	tCount=$2

	if [[ -d  ${tUCArg} ]]; then
		echo Entering to the UC ${tUCArg}
		cd ${tUCArg}
	else
		echo "The specified UC ${tUCArg} is not found ! "
		return 1
	fi

	## Fetch the Generic Profile list
	for tProfileName in "${vPROFILE_NAMES[@]}"
	do
		pwd
		echo "tProfileName: ${tProfileName}"

		## Fetch the Robot files list under UC
		tTS=${vTEST_SCENARIO_LOCATION}/${tUCArg}/*.robot

		## Fetch the cfg list for the given Robot File
		for tRobot in $tTS
		do
			tmp=$(basename $tRobot)
			tRobotName=${tmp%.*}
			cFlag=0

			# If config folder is missing, then look for default cfg
			if [[ ! -d ${vTEST_SCENARIO_LOCATION}/${tUCArg}/${tRobotName} ]]; then
				echo "Config folder ${tRobotName} is not present, looking for default configurations"
				mkdir -v ${vTEST_SCENARIO_LOCATION}/${tUCArg}/${tRobotName}
				cFlag=0
				tDefCfg=${vTEST_SCENARIO_LOCATION}/${tUCArg}/${tRobotName}/default.cfg
				if [[ ! -f ${tDefCfg} ]]; then
					echo "Default file is missing, copying default.cfg from config"
					cp ${vCFG_TEMPLATE_LOCATION}/default.cfg ${tDefCfg}
				fi
				tTSCfg=${tDefCfg}
			else
				vTestConfFilter=${vTEST_SCENARIO_LOCATION}/${tUCArg}/${tRobotName}/${vROBOT_CFG_FILER}
				if [[ -s ${vTestConfFilter} ]]; then
					tempcfg=(`cat ${vTestConfFilter} | grep -i ^CFG= |  sed 's/CFG=//' | sed 's/:[0-9]*//g' | sed 's/\://g'`);
					tTSCfg=${tempcfg[@]}
					echo "fnTaskExecuteRobot: Picking filtered cfg list: " ${tTSCfg}
				else
					tTSCfg=${vTEST_SCENARIO_LOCATION}/${tUCArg}/${tRobotName}/*.cfg
				fi
			fi

			for tCfg in ${tTSCfg}
			do
				tmp=$(basename $tCfg)
				tCfgName=${tmp%.*}
				fnCallToRobot ${tProfileName} ${tUCArg} ${tRobotName} ${tCfgName} ${tCount}

				# Full Execution or Partial execution.
				tTestExec=${tRobotName}-${tCfgName}-${tProfileName}
				echo "vROBOT_STOP_ONFAIL: ${vROBOT_STOP_ONFAIL}"
				echo "Test status: ${vResultArray["${tTestExec}"]}"
				if [ ${vROBOT_STOP_ONFAIL} == "True" ] && [ ${vResultArray["${tTestExec}"]} == "Fail" ]; then
					echo "fnTaskExecuteRobot: Observed a failure in the execution and the Partial execution enabled"
					echo "fnTaskExecuteRobot: Robot execution will be terminated !!"
					tFlag=true
					break
				fi

				if [ ! -z ${vTC_TEST_DELAY} ];then
					echo "Delay between test: ${vTC_TEST_DELAY} sec"
					sleep ${vTC_TEST_DELAY}
				fi
			done
			if [ ${cFlag} -eq 1 ]; then
				rm -rf ${vTEST_SCENARIO_LOCATION}/${tUCArg}/${tRobotName}
			fi
			if [ ${tFlag} == true ];then
				break;
			fi
		done
		if [ ${tFlag} == true ];then
			break;
		fi
	done
}

## Function definition to retry the execution on failure scenario
##
function fnCallToRobotRetry {
	tProfileName=$1
	tUCArg=$2
	tRobotName=$3
	tCfgName=$4
	tCount=$5

	tTestExec=${tRobotName}-${tCfgName}-${tProfileName}

	echo "Test execution retry: ${tTestExec}"

	# Call to Robot
	robot										\
		-v ${vROBOT_VARIABLE_1}:${vUC_ITERATIONS[$tCount]}			\
		-v ${vROBOT_VARIABLE_2}:${tRobotName}/${tCfgName}.cfg			\
		-V ${vProfileDir}/${tProfileName}.py					\
		   ${vROBOT_TAGS_OPT}							\
		-d ../../testArtifacts/reports/${tUCArg}				\
		--rerunfailed ../../testArtifacts/reports/${tUCArg}/${tTestExec}.xml	\
		-r ${tTestExec}.html							\
		-l log_${tTestExec}.html						\
		   ${tRobotName}.robot
	ret=$?

	# Update global variable
	retryRet=$ret
}

## Function definition to execute the robot iteratively
##
function fnCallToRobot {
	tProfileName=$1
	tUCArg=$2
	tRobotName=$3
	tCfgName=$4
	tCount=$5

	tTestExec=${tRobotName}-${tCfgName}-${tProfileName}
	echo "fnCallToRobot: Test execution strated for ${tUCArg}:${vUC_ITERATIONS[$tCount]} with combination ${tTestExec}"

	# Call to Robot
	robot								\
		-v ${vROBOT_VARIABLE_1}:${vUC_ITERATIONS[$tCount]}	\
		-v ${vROBOT_VARIABLE_2}:${tRobotName}/${tCfgName}.cfg	\
		-V ${vProfileDir}/${tProfileName}.py			\
		   ${vROBOT_TAGS_OPT}					\
		-d ../../testArtifacts/reports/${tUCArg}		\
		-o ${tTestExec}.xml					\
		-r ${tTestExec}.html					\
		-l log_${tTestExec}.html				\
		   ${tRobotName}.robot
	ret=$?

	if [ $ret -ne 0 ] && [ ${vROBOT_RETRY_ONFAIL} == "True" ]; then
		for i in `seq 1 ${vROBOT_RETRY_COUNT}`;
		do
			echo "Retry count $i"
			fnCallToRobotRetry ${tProfileName} ${tUCArg} ${tRobotName} ${tCfgName} ${tCount}
			if [ $retryRet -ne 0 ]; then
				ret=1
				echo "Test failed on retry"
			else
				ret=0
				echo "Test passed on retry"
				break;
			fi
		done
	fi

	if [ $ret -ne 0 ]; then
		vResultArray["${tTestExec}"]="Fail"
		((vROBOT_FAIL_COUNT++));
		echo "fnCallToRobot: Test execution has failed for the UC: ${tTestExec}."
		echo "fnCallToRobot: Please check the report/log for more information !!!"
	else
		vResultArray["${tTestExec}"]="Pass"
		((vROBOT_PASS_COUNT++));
		echo "fnCallToRobot: Test Execution PASS for ${tTestExec}"
	fi

	echo "Status for $tUCArg in fnTaskExecuteRobot: ${vResultArray["${tTestExec}"]}"
}

##  Function to initiate the robot execution
##
function fnExecuteRobot {
	echo "fnExecuteRobot: Test execution"
	cd ${vTEST_SCENARIO_LOCATION}
	pwd
	count=0

	for tArr in "${vUC_NAMES[@]}"
	do
		echo "Executing robot operation"
		fnTaskExecuteRobot ${tArr} $count
                
		((count++));
		cd ${vTEST_SCENARIO_LOCATION}

		if [ ${tFlag} == true ];then
			break;
		fi
	done

	echo "Robot execution thread is completed"
}

## Function calls Starts here
##
fnExecuteRobot
fnPlaceReports
#fnFormatText
