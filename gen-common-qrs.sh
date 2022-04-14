TMPF=$(mktemp)
seq 0 200 | while read a; do
    echo -n " $a"
    qrencode -t eps -v 1 -l H -o $TMPF $a < /dev/null
    epspdf --pdfversion 1.5 $TMPF common/numbers/$a.pdf
done
