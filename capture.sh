# $1 is the output filepath to write the capture to (.pcap)
# $2 is the stream capture time
# $3 is the interface name

rm $1
touch $1
chmod a+w $1
sudo tshark -i $3 -a duration:$2 -w $1 2> /dev/null &