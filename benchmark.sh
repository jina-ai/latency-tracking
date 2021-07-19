#!/usr/bin/python3

mkdir -p output

for file in benchmarks/*.py; do
    output_json=$(echo $file | sed -r 's/.py/.json/g' | sed -r 's/benchmarks/output/g')
    output_plot=$(echo $file | sed -r 's/.py/.png/g' | sed -r 's/benchmarks/output/g')
    cmdbench --save-json=${output_json} --save-plot=${output_plot} python3 ${file}
done