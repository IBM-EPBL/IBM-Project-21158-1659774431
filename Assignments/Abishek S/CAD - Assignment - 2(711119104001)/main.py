connect to database

import ibm_db
try:
    ibm_db.connect("DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;PROTOCOL=TCPIP;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=qzy32417; PWD=xEZZ5b9Q71LQIKIR;", "", "")
     print("connected")
except:
    print("not connected")          