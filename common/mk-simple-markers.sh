
SIZE=7

function foo()
{
NN=$1
shift

echo -n "convert -size ${SIZE}x$SIZE xc:white -fill black "

SIZEM0=$(( $SIZE - 0 ))
SIZEM1=$(( $SIZE - 1 ))
SIZEM2=$(( $SIZE - 2 ))


#THIS IS WAAAY Overkill, a simple bitstring would do but bash... dunno
HH=$(echo "FOOBAR $NN" | openssl dgst -blake2b512 -hex -r | cut -d" " -f 1)


co=$(( $SIZEM0 * $SIZEM0))
while [[ $co -ge 0 ]]; do
    t=${HH:$co:1}
    l=$(( $co / $SIZEM0 + 0))
    c=$(( $co % $SIZEM0 + 0))
    if [[ "$t" > "7" ]]; then
        echo -n " -draw 'point $l,$c'"
        true
    fi
    co=$(( $co - 1 ))
done

echo -n " -draw 'point 0,0'"
echo -n " -draw 'point $SIZEM1,0'"
echo -n " -draw 'point 0, $SIZEM1'"
echo -n " -draw 'point $SIZEM1,$SIZEM1'"

HALF=$(($SIZE / 2))
for i in -1 0 1; do
for j in -1 0 1; do
    x=$(( $HALF + $i ))
    y=$(( $HALF + $j ))
    echo -n " -draw 'point $x,$y'"
done
done

#co=$SIZEM1
#while [[ $co -ge 0 ]]; do
#        echo -n " -draw 'point $co,$co'"
#        #echo -n " -draw 'point $co, $SIZEM1'"
#    co=$(( $co - 1 ))
#done

echo -n " out/$NN.png"
echo
echo "convert out/$NN.png -border 2 -scale 1000% out/${NN}_1000.png"
}

mkdir -p out/

foo "0" 
foo "1" 
foo "2" 
foo "3"
