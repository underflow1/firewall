:if ([/interface list get "intralan forward"] true) do={/interface list remove "intralan forward"}
/interface list add comment="intralan forward" exclude=WAN,LAN include=all name="intralan forward"
