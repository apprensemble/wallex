#!/usr/bin/bash

# ref repositories
testRep=./tests/
libRep=./myblockscoutlib/

# info about new lib to add
new_url="https://explorer.mantle.xyz"
new_lib_file=$libRep"mantle.py"
new_lib="mantle"
new_test_file=$testRep"test_mantle.py"
new_combo_file=$testRep"test_combo_cmc_mantle.py"

# info about old ref lib to copy
old_url="https://base.blockscout.com" 
old_lib_file=$libRep"base.py"
old_lib="base"
old_test_file=$testRep"test_base.py"
old_combo_file=$testRep"test_combo_cmc_base.py"
#make lib
sed "s#$old_url#$new_url#g" $old_lib_file > $new_lib_file

#make test lib
sed "s#$old_lib#$new_lib#g" $old_test_file > $new_test_file

#make combo test
sed "s#$old_lib#$new_lib#g" $old_combo_file > $new_combo_file


