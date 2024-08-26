#!/usr/bin/bash

echo "choix du nom de lib de destination"
read destination
echo "creation LIB $destination"
echo "choix de l'url de la nouvelle API"
read new_url 

if [ "${#new_url}" == 0 ];then 
new_url="https://${destination}.blockscout.com" 
fi
echo "url de l'API: ${new_url}"

# ref repositories
testRep=./tests/
libRep=./myblockscoutlib/
ref="base"

# info about old lib to add as new dest lib
old_url="https://${ref}.blockscout.com" 
old_lib_file=$libRep"${ref}.py"
old_lib="${ref}"
old_test_file=$testRep"test_${ref}.py"

new_lib_file=$libRep"${destination}.py"
new_lib="${destination}"
new_test_file=$testRep"test_${destination}.py"

echo "ref:"
echo $old_url
echo $old_lib_file
echo $old_lib
echo $old_test_file

echo "destination:"
echo $new_url
echo $new_lib_file
echo $new_lib
echo $new_test_file

echo "pause"
read


#make lib
sed "s#$old_url#$new_url#g" $old_lib_file > $new_lib_file

#make test lib
sed "s#$old_lib#$new_lib#g" $old_test_file > $new_test_file


