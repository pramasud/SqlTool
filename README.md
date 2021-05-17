# SqlTool
Utility to extract metadata from Oracle PLSQL package bodies and Deploy DML Scripts to Oracle DB.

To connect to Oracle database, please download Instant Client for the following location
https://www.oracle.com/in/database/technologies/instant-client/microsoft-windows-32-downloads.html

Download instantclient-basic-nt-19.10.0.0.0dbru.zip -> unzip -> Copy all contents from inside instantclient_19_10 into $APPHOME/OracleClient/Client
Folder Structure should look like :
$APPHOME
    -> cfg
    -> Log
    -> OracleClient
        -> Client
    -> Out
    -> src
    
Main Page:

![image](https://user-images.githubusercontent.com/44316307/118475202-94079880-b729-11eb-8f81-898a7278bf38.png)

Settings:

![image](https://user-images.githubusercontent.com/44316307/118475277-aeda0d00-b729-11eb-9ffa-ca310ea628db.png)

Process button to extract metadata from all package bodies found under the selected directory (Search recursively).

![image](https://user-images.githubusercontent.com/44316307/118475950-8b639200-b72a-11eb-86fd-9ffae0050c39.png)

List files button will list all files under the directory recursively, Full file path will be displayed if Show Full Path Radio is checked.
![image](https://user-images.githubusercontent.com/44316307/118476436-1fcdf480-b72b-11eb-8004-99483739e077.png)

Execute in Oracle and Deploy JS UIXML files will deploy the files as defined in the settings.

