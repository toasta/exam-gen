
SIZE=7

function foo()
{
NN=$1
shift

echo -n "convert -size ${SIZE}x$SIZE xc:white -fill black "

SIZEM1=$(( $SIZE - 1 ))


#THIS IS WAAAY Overkill, a simple bitstring would do but bash... dunno
HH=$(echo "FOOBAR $NN" | openssl dgst -blake2b512 -hex -r | cut -d" " -f 1)


co=$(( $SIZEM1 * $SIZEM1 - 1))
while [[ $co -ge 0 ]]; do
    t=${HH:$co:1}
    l=$(( $co / $SIZEM1 + 1))
    c=$(( $co % $SIZEM1 + 0))
    if [[ "$t" > "7" ]]; then
        echo -n " -draw 'point $l,$c'"
        true
    fi
    co=$(( $co - 1 ))
done

co=$SIZEM1
while [[ $co -ge 0 ]]; do
    if [[ $(( $co % 2 )) == 0 ]]; then
        echo -n " -draw 'point 0,$co'"
        echo -n " -draw 'point $co, $SIZEM1'"
    fi
    co=$(( $co - 1 ))
done

echo -n " out/$NN.png"
echo
echo "convert out/$NN.png -border 2 -scale 1000% out/${NN}_1000.png"
}

mkdir -p out/

foo "0" 
foo "1" 
foo "2" 
foo "3"
