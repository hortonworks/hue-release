echo "Start zeroing:"
for dir in `mount | grep ext | awk '{ print $3 }'`; do
    echo "... $dir"
    dd if=/dev/zero >> "$dir/zero" 2>/dev/null
    rm -f "$dir/zero";
    echo "DONE"
    echo
done
echo
df
