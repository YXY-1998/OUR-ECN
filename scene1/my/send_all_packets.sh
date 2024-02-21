echo "Sending ip packets on all VLs" & exec mx h1 python send.py 10.0.2.5 & exec mx h2 python send.py 10.0.2.5 & exec mx h3 python send.py 10.0.2.5 
