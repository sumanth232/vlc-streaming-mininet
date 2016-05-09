
rm temp.pcap 2> /dev/null
tshark -r $1 -Y "((ip.addr eq $2 and ip.addr eq $3) and (udp.port eq $4))" -w temp.pcap
bitrate=$(capinfos -i temp.pcap | grep "Data bit rate" | grep -o -E "[0-9].+ " | cut -f1 -d' ')

# duration = capture duration = time between first and last packet
duration=$(capinfos -u temp.pcap | grep "Capture duration" | grep -o -E "[0-9]+ " | cut -f1 -d' ')

packetCount=$(capinfos -c temp.pcap | grep "Number of packets" | grep -o -E "[0-9]+ " | cut -f1 -d' ')

# echo ${bitrate}
# echo ${duration}

packetDelay=$(echo "$duration*1000/$packetCount" | bc -l)

str=${bitrate}':'${packetDelay}
echo ${str}

