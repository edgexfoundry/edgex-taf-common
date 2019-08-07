#!/bin/bash

vPROJ_CONF=$1
vTEXT="$2"

function fnExtractConf {
        temp=("`cat ${vPROJ_CONF} | grep -i ${vTEXT}: | sed "s/\${vTEXT}://"`");
        echo ${temp}
}

result=$(fnExtractConf vTEXT)
echo ${result}

if [[ ${result} == 'Fail' ]];then
	exit 1
elif [[ ${result} == 'Pass' ]];then
	exit 0
else
	exit 2
fi
