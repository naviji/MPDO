higher=4
seed=6

python3 test.py $seed $higher 

while [[ $? -eq 1 ]]; do
    higher=$(($higher*2))
    python3 test.py $seed $higher
done
echo higher is $higher

lower=$(($higher/2))
while [[ lower -lt higher ]]; do
    mid=$((($lower+$higher)/2))
    echo lower is $lower
    echo mid is $mid
    echo higher is $higher
    python3 test.py $seed $mid
    if [[ $? -eq 1 ]]
    then
        lower=$(($mid+1))
    else
        higher=$(($mid-1))
    fi
done
echo optimal is $mid
