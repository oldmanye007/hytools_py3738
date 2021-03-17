#!/bin/bash

imgspec_dir=$( cd "$(dirname "$0")" ; pwd -P )
hytools_dir=$(dirname $imgspec_dir)

input="input"
mkdir -p output

# Get input paths
rfl_files=$(python ${imgspec_dir}/get_paths_from_granules.py -p rfl)
echo "Found input reflectance file(s): $rfl_files"
obs_ort_files=$(python ${imgspec_dir}/get_paths_from_granules.py -p obs_ort)
echo "Found input observation file(s): $obs_ort_files"

# Create image_correct_config
python get_from_context.py image_correct_config > image_correct_config.json
echo "Created image_correct_config.json file from \"image_correct_config\" parameter"
python $imgspec_dir/update_config.py image_correct_config.json image_correct $rfl_files $obs_ort_files
echo "Updated image_correct_config.json with input paths"

# Execute hytools image correction
image_correct_cmd="python $hytools_dir/scripts/image_correct.py image_correct_config.json"
echo "Executing cmd: $image_correct_cmd"
${image_correct_cmd}

# Copy coeffs files to input directory for trait estimate step
# echo "Copying coefficients files to input directory..."
# cp output/*{topo,brdf}_coeffs*json input/<_topo_brdf dir>/

# Create trait_estimate_config
python get_from_context.py trait_estimate_config > trait_estimate_config.json
echo "Created trait_estimate_config.json file from \"trait_estimate_config\" parameter"
python $imgspec_dir/update_config.py trait_estimate_config.json trait_estimate $rfl_files $obs_ort_files
echo "Updated trait_estimate_config.json with input paths, coeffs paths, and trait model paths"

# Execute hytools image correction
trait_estimate_cmd="python $hytools_dir/scripts/trait_estimate.py trait_estimate_config.json"
echo "Executing cmd: $trait_estimate_cmd"
${trait_estimate_cmd}