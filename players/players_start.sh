#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <number_of_players>"
    exit 1
fi

num_players=$1
pids=()

for ((i=1; i<=$num_players; i++))
do
    python3 client.py &
    pids+=($!)
done

read -p "Press Enter to exit..."

for pid in "${pids[@]}"
do
    kill $pid
    wait $pid 2>/dev/null
done

