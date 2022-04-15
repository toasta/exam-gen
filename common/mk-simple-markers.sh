
SIZE=6

function foo()
{
NN=$1
shift
PX=$1
shift
PY=$1
shift

echo -n "convert -size ${SIZE}x$SIZE xc:white -fill black "

SIZEM1=$(( $SIZE - 1 ))

seq 0 5 | while read a; do
    echo -n " -draw 'point 0,$a'"
    echo -n " -draw 'point $SIZEM1,$a'"
    echo -n " -draw 'point $a,0'"
    echo -n " -draw 'point $a,$SIZEM1'"
done

for i in 1 2 ; do
    for j in 1 2; do
        echo -n " -draw 'point $(( $PX + $i)),$(( $PY + $j))'"
    done
done
echo -n " out/$NN.tiff"
echo
echo "convert out/$NN.tiff -border 2 -scale 1000% out/${NN}_1000.tiff"
}

mkdir -p out/

foo "0" "0" "0"
foo "1" "2" "0"
foo "2" "0" "2"
foo "3" "2" "2"
