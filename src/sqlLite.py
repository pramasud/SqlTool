import sqlite3
### Get Value
def getParamValue(param_group, param_name, database):
    #print(database)
    conn = sqlite3.connect(database)
    c = conn.cursor()
    m = ('table', 'sqltool_settings')
    c.execute('SELECT count(*) FROM sqlite_master WHERE type=? and name=?', m)
    x = c.fetchone()
    if x[0] == 1:
        t = (param_group.upper(),param_name.upper(),'A')
        c.execute('SELECT param_value FROM sqltool_settings WHERE function=? and param_name=? and status=?', t)
        p = c.fetchone()
        if p:
            value = p[0]
        else:
            value = "Not_Found"
    else:
        c.execute('''CREATE TABLE sqltool_settings (function text, param_name text, param_value text, status text)''')
        conn.commit()
        value = "Not_Found"

    conn.close()
    return value

### Update or Insert Value
def setParamValue(param_group, param_name, param_value, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    i = (param_group.upper(),param_name.upper(),param_value,'A')
    m = ('table','sqltool_settings')
    c.execute('SELECT count(*) FROM sqlite_master WHERE type=? and name=?',m)
    x = c.fetchone()
    if x[0] == 1:
        t = (param_group.upper(),param_name.upper(),'A')
        c.execute('SELECT param_value FROM sqltool_settings WHERE function=? and param_name=? and status=?', t)
        p = c.fetchone()
        if p:
            t = (param_value,param_group.upper(),param_name.upper(),'A')
            c.execute('UPDATE sqltool_settings SET param_value = ? WHERE function=? and param_name=? and status=?', t)
            conn.commit()
        else:
            t = (param_group.upper(),param_name.upper(),param_value,'A')
            c.execute('INSERT INTO sqltool_settings VALUES (?,?,?,?)', t)
            conn.commit()
    else:
        c.execute('''CREATE TABLE sqltool_settings (function text, param_name text, param_value text, status text)''')
        c.execute('INSERT INTO sqltool_settings VALUES (?,?,?,?)', i)
        conn.commit()

    conn.close()

def delParamRec(param_group, param_name, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    m = ('table','sqltool_settings')
    c.execute('SELECT count(*) FROM sqlite_master WHERE type=? and name=?',m)
    x = c.fetchone()
    if x[0] == 1:
        t = (param_group.upper(),param_name.upper(),'A')
        c.execute('DELETE FROM sqltool_settings WHERE function=? and param_name=? and status=?', t)
        conn.commit()
    conn.close()


def getPassword(os_user, db_sid, db_user, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    m = ('table', 'sqltool_pwd')
    c.execute('SELECT count(*) FROM sqlite_master WHERE type=? and name=?', m)
    x = c.fetchone()
    if x[0] == 1:
        t = (os_user.upper(), db_sid.upper(), db_user.upper())
        c.execute('SELECT password FROM sqltool_pwd WHERE os_user=? and db_sid=? and db_user=?', t)
        p = c.fetchone()
        if p:
            value = p[0]
        else:
            value = "Not_Found"
    else:
        c.execute('''CREATE TABLE sqltool_pwd (os_user text, db_sid text, db_user text, password text)''')
        conn.commit()
        value = "Not_Found"

    conn.close()
    return value


### Update or Insert Value
def setPassword(os_user, db_sid, db_user, password, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    i = (os_user.upper(), db_sid.upper(), db_user.upper(), password)
    m = ('table', 'sqltool_pwd')
    c.execute('SELECT count(*) FROM sqlite_master WHERE type=? and name=?', m)
    x = c.fetchone()
    if x[0] == 1:
        t = (os_user.upper(), db_sid.upper(), db_user.upper())
        c.execute('SELECT password FROM sqltool_pwd WHERE os_user=? and db_sid=? and db_user=?', t)
        p = c.fetchone()
        if p:
            t = (password, os_user.upper(), db_sid.upper(), db_user.upper())
            c.execute('UPDATE sqltool_pwd SET password = ? WHERE os_user=? and db_sid=? and db_user=?', t)
            conn.commit()
        else:
            t = (os_user.upper(), db_sid.upper(), db_user.upper(), password)
            c.execute('INSERT INTO sqltool_pwd VALUES (?,?,?,?)', t)
            conn.commit()
    else:
        c.execute('''CREATE TABLE sqltool_pwd (os_user text, db_sid text, db_user text, password text)''')
        c.execute('INSERT INTO sqltool_pwd VALUES (?,?,?,?)', i)
        conn.commit()

    conn.close()
    
### Update or Insert Value
def delPassword(os_user, db_sid, db_user, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    i = (os_user.upper(), db_sid.upper(), db_user.upper())
    m = ('table', 'sqltool_pwd')
    c.execute('SELECT count(*) FROM sqlite_master WHERE type=? and name=?', m)
    x = c.fetchone()
    if x[0] == 1:
        t = (os_user.upper(), db_sid.upper(), db_user.upper())
        c.execute('DELETE FROM sqltool_pwd WHERE os_user=? and db_sid=? and db_user=?', t)
        conn.commit()
    else:
        c.execute('''CREATE TABLE sqltool_pwd (os_user text, db_sid text, db_user text, password text)''')
        conn.commit()

    conn.close()

def delAllPasswords(database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    m = ('table', 'sqltool_pwd')
    c.execute('SELECT count(*) FROM sqlite_master WHERE type=? and name=?', m)
    x = c.fetchone()
    if x[0] == 1:
        c.execute('DELETE FROM sqltool_pwd')
        conn.commit()
    conn.close()

def getParamValueList(param_group, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    m = ('table', 'sqltool_settings')
    c.execute('SELECT count(*) FROM sqlite_master WHERE type=? and name=?', m)
    x = c.fetchone()
    if x[0] == 1:
        t = (param_group.upper(),'A')
        c.execute('SELECT param_value FROM sqltool_settings WHERE function=? and status=?', t)
        p = c.fetchall()
        #value = p
        value = []
        for data in p:
            value.append(data[0])
    else:
        c.execute('''CREATE TABLE sqltool_settings (function text, param_name text, param_value text, status text)''')
        conn.commit()
        value = "Not_Found"

    conn.close()
    return value

#setParamValue("DATABASESERVER", "DEV","Dev", "cfg\\settings.db")
#setParamValue("JSUIXMLSERVER", "IUT","IUT", "cfg\\settings.db")
#setParamValue("JSUIXMLSERVER", "CRE","CRE", "cfg\\settings.db")
#setParamValue("JSUIXMLSERVER", "OATS","OATS", "cfg\\settings.db")
#setParamValue("JSUIXMLSERVER", "CRE2","CRE2", "cfg\\settings.db")

#setParamValue("JSPATH", "DEV", "C:\\", "cfg\\settings.db")
#setParamValue("UIXMLPATH", "DEV","D:\\", "cfg\\settings.db")

#var = getParamValueList("JSUIXMLSERVER", "cfg\\settings.db")
#print(var)
#delParamRec("DATABASESERVER", "DEV", "cfg\\settings.db")
