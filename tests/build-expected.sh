#!/bin/bash

cd "$(dirname "$0")"
for FILE in expected_*.html
do
    OLD=${FILE%.html}.old
    mv -n "${FILE}" "${OLD}"
done

efj logbook < convert_test_input > expected_logbook.html
efj logbook -f 20240103 < convert_test_input > expected_logbook_from.html
efj logbook -t 20240103 < convert_test_input > expected_logbook_to.html
efj logbook -f 20240102 -t 20240103 < convert_test_input > expected_logbook_fromto.html

efj cumulative < convert_test_input > expected_cumulative.html
efj cumulative -f 20240103 < convert_test_input > expected_cumulative_from.html
efj cumulative -t 20240103 < convert_test_input > expected_cumulative_to.html
efj cumulative -f 20240102 -t 20240103 < convert_test_input > expected_cumulative_fromto.html

efj summary < convert_test_input > expected_summary.html
efj summary -f 20240103 < convert_test_input > expected_summary_from.html
efj summary -t 20240103 < convert_test_input > expected_summary_to.html
efj summary -f 20240102 -t 20240103 < convert_test_input > expected_summary_fromto.html

for FILE in expected_*.html
do
    OLD=${FILE%.html}.old
    cmp "${FILE}" "${OLD}"
    if [ $? -eq 0 ]
    then
        rm ${OLD}
    fi
done

echo CHECK MODIFIED FILES ARE CORRECT EXPECTED OUTPUT!!!
