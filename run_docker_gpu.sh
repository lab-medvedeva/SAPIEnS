docker run --rm --runtime=nvidia -it \
    --mount "type=bind,src=$PWD/../SCALE_data,dst=/home/ubuntu/data" \
    --mount "type=bind,src=$PWD/../SCALE_results,dst=/home/ubuntu/results" \
    scale bash
