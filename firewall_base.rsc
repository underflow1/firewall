#BASE FIREWALL
/ip firewall filter
# BASE DROP
/ip firewall filter add action=drop chain=input comment="BASE DROP INVALID INPUT" connection-state=invalid in-interface-list=WAN log-prefix=!INPUT 
add action=drop chain=forward comment="BASE DROP INVALID FORWARD" connection-state=invalid 
# BASE FAIL2BAN
add action=drop chain=input dst-port=22,2222,2223 protocol=tcp src-address=!192.168.80.212 src-address-list=ssh_blacklist comment="BASE FAIL2BAN 000" 
add action=add-src-to-address-list address-list=ssh_blacklist address-list-timeout=10m chain=input \
    connection-state=new dst-port=22,2222,2223 protocol=tcp src-address-list=ssh_stage4 comment="BASE FAIL2BAN 001" 
add action=add-src-to-address-list address-list=ssh_stage4 address-list-timeout=1m chain=input \
    connection-state=new dst-port=22,2222,2223 protocol=tcp src-address-list=ssh_stage3 comment="BASE FAIL2BAN 002" 
add action=add-src-to-address-list address-list=ssh_stage3 address-list-timeout=1m chain=input \
    connection-state=new dst-port=22,2222,2223 protocol=tcp src-address-list=ssh_stage2 comment="BASE FAIL2BAN 003" 
add action=add-src-to-address-list address-list=ssh_stage2 address-list-timeout=1m chain=input \
    connection-state=new dst-port=22,2222,2223 protocol=tcp src-address-list=ssh_stage1 comment="BASE FAIL2BAN 004" 
add action=add-src-to-address-list address-list=ssh_stage1 address-list-timeout=1m chain=input \
    connection-state=new dst-port=22,2222,2223 protocol=tcp comment="BASE FAIL2BAN 005" 
# BASE KNOCKING...
add action=accept chain=input comment="BASE KNOCKING 000" dst-port=2222,2223 in-interface-list=WAN protocol=tcp src-address-list=mkrt03 
add action=add-src-to-address-list address-list=mkrt01 address-list-timeout=1m chain=input comment="BASE KNOCKING 001" in-interface-list=WAN packet-size=328 protocol=icmp 
add action=add-src-to-address-list address-list=mkrt02 address-list-timeout=1m chain=input comment="BASE KNOCKING 002" in-interface-list=WAN packet-size=428 protocol=icmp src-address-list=mkrt01 
add action=add-src-to-address-list address-list=mkrt03 address-list-timeout=30m chain=input comment="BASE KNOCKING 003" in-interface-list=WAN packet-size=228 protocol=icmp src-address-list=mkrt02 
add action=accept chain=input comment="BASE KNOCKING 004 ECHO REQUEST" icmp-options=8:0 in-interface-list=WAN protocol=icmp 

# BASE ESTABLISHED,RELATED,UNTRACKED INPUT
add action=accept chain=input comment="BASE ESTABLISHED,RELATED,UNTRACKED" connection-state=established,related,untracked in-interface-list=WAN
# BASE ESTABLISHED,RELATED,UNTRACKED FORWARD
add action=accept chain=forward comment="BASE ESTABLISHED,RELATED,UNTRACKED" connection-state=established,related,untracked
# BASE GRE
add action=accept chain=input comment="BASE GRE" in-interface-list=WAN protocol=gre 
# BASE IPSEC
add action=accept chain=input comment="BASE IPSEC" in-interface-list=WAN protocol=ipsec-esp 
add action=accept chain=input comment="BASE IPSEC" dst-port=500,4500 in-interface-list=WAN protocol=udp 
# BASE L2TP
add action=accept chain=input comment="BASE L2TP" dst-port=1701 in-interface-list=WAN protocol=udp 
add action=accept chain=input comment="BASE L2TP" dst-port=1701 in-interface-list=WAN protocol=tcp 
# BASE SSTP
add action=accept chain=input comment="BASE SSTP" dst-port=4443 in-interface-list=WAN protocol=tcp 
# BASE INTRALAN FORWARD
add action=accept chain=forward comment="BASE INTRALAN FORWARD" in-interface-list="intralan forward" out-interface-list="intralan forward"
# BASE FORWARD
add action=accept chain=forward comment="BASE FORWARD" in-interface-list=LAN out-interface-list="intralan forward"

