import psycopg2
import json
import os

def createTable():
    '''
    每次调用此方法，将删除所有的表后再创建。表格式如下：

    Table project
    {
        id       int PK,
        name     string NOT NULL,
        version  string NOT NULL,
        enabled  boolean,
        language string NOT NULL,
        iconHref string
    }
    Table classItem
    {
        id         int PK,
        fullName   string NOT NULL,
        simpleName string NOT NULL,
        href       string NOT NULL,
        projectId  int
    }

    Table methodItem
    {
        id          int PK,
        classItemId int,
        signName    string NOT NULL,
        href        string NOT NULL,
        type        string NOT NULL
    }

    Table fieldItem
    {
        id          int PK,
        classItemId int,
        filedName   string NOT NULL,
        href        string NOT NULL
    }
    '''
    conn = getConnection()
    tables = ['METHODITEM', 'FIELDITEM', 'CLASSITEM', 'PROJECT']
    for table in tables:
        cursor = conn.cursor()
        try:
            cursor.execute("DROP TABLE %s;" % table)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
        finally:
            cursor.close()

    curs = conn.cursor()
    try:
        curs.execute("CREATE TABLE PROJECT ("
                        "ID SERIAL PRIMARY KEY,"
                        "NAME VARCHAR(200) NOT NULL,"
                        "VERSION VARCHAR(50) NOT NULL,"
                        "ENABLED BOOLEAN,"
                        "LANGUAGE VARCHAR(50) NOT NULL,"
                        "ICONHREF VARCHAR(1000)"
                     ");"
                     "ALTER TABLE PROJECT ADD CONSTRAINT "
                     "UNIQUE_GOODS_SID UNIQUE(NAME, VERSION);"
                     "CREATE TABLE CLASSITEM ("
                        "ID SERIAL PRIMARY KEY,"
                        "FULLNAME VARCHAR(200) NOT NULL,"
                        "SIMPLENAME VARCHAR(100) NOT NULL,"
                        "HREF VARCHAR(1000) NOT NULL,"
                        "PROJECTID INT"
                     ");"
                     "ALTER TABLE CLASSITEM ADD FOREIGN KEY(PROJECTID) "
                     "REFERENCES PROJECT(ID) "
                     "ON DELETE CASCADE ON UPDATE RESTRICT;"
                     "CREATE TABLE METHODITEM ("
                        "ID SERIAL PRIMARY KEY,"
                        "CLASSITEMID INT,"
                        "SIGNNAME VARCHAR(1000) NOT NULL,"
                        "HREF VARCHAR(1000) NOT NULL,"
                        "TYPE VARCHAR(20)"
                     ");"
                     "ALTER TABLE METHODITEM ADD FOREIGN KEY(CLASSITEMID) "
                     "REFERENCES CLASSITEM(ID) "
                     "ON DELETE CASCADE ON UPDATE CASCADE;"
                     "CREATE TABLE FIELDITEM ("
                        "ID SERIAL PRIMARY KEY,"
                        "CLASSITEMID INT,"
                        "FILEDNAME VARCHAR(50) NOT NULL,"
                        "HREF VARCHAR(1000) NOT NULL"
                     ");"
                     "ALTER TABLE FIELDITEM ADD FOREIGN KEY(CLASSITEMID) "
                     "REFERENCES CLASSITEM(ID) "
                     "ON DELETE CASCADE ON UPDATE CASCADE;"
                    )
        conn.commit()
    except Exception as e:
        raise(e)
    finally:
        curs.close()
        conn.close()

def getConnection():
    config = '%s/%s' % (os.getcwd(), 'config.json')
    data = {'database':'', 'user':'postgres', 'password':'postgres', 'host':'localhost', 'port':'5432'}
    if os.path.exists(config):
        with open(config, 'r') as f:
            m = json.load(f)['postgresql']
            for k, v in m.items():
                data[k] = m[k]

    return psycopg2.connect(database=data['database'], user=data['user'], password=data['password'], host=data['host'], port=data['port'])

def searchAllProjectName():
    sql = 'SELECT * FROM project'
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql)
    return list(cursor.fetchall())

def searchDB(key, projectId=None):
    fullNameSql   = "SELECT 'clazz', p.iconhref, c.id, c.fullname, c.href FROM classitem AS c LEFT JOIN project AS p ON p.id = c.projectid WHERE p.enabled = true AND c.fullname ILIKE %s"
    simpleNameSql = "SELECT 'clazz', p.iconhref, c.id, c.simpleName, c.href FROM classitem AS c LEFT JOIN project AS p ON p.id = c.projectid WHERE p.enabled = true AND c.simpleName ILIKE %s"
    methodSql     = "SELECT 'method', p.iconhref, m.id, m.signname, m.href FROM methoditem AS m LEFT JOIN classitem AS c ON m.classitemid = c.id LEFT JOIN project AS p ON p.id = c.projectid WHERE p.enabled = true AND m.signname ilike %s"
    fieldSql      = "SELECT 'field', p.iconhref, f.id, f.filedname, f.href FROM fielditem AS f LEFT JOIN classitem AS c ON f.classitemid = c.id LEFT JOIN project AS p ON p.id = c.projectid WHERE p.enabled = true AND f.filedname ilike %s"

    result = []
    for sql in (fullNameSql, simpleNameSql, methodSql, fieldSql):
        result.extend(__templeSearch(sql, key, projectId))
    return result

def convertItemToTableName(item):
    m = {'clazz': 'CLASSITEM', 'method': 'METHODITEM', 'field': 'FIELDITEM'}
    return m[item] if m.has_key(item) else item

def detailed(item, key):
    cId = ''
    if item != 'clazz':
        cId = 'select CLASSITEMID from %s where id = %s' % convertItemToTableName(item), key
    else:
        cId = key

    csql = "select SIGNNAME, HREF from METHODITEM where CLASSITEMID = %s and TYPE = 'constructor'"
    msql = "select SIGNNAME, HREF from METHODITEM where CLASSITEMID = %s"
    fsql = "select FILEDNAME, HREF from FIELDITEM where CLASSITEMID = %s"
    return [__templeSearchDetailed(sql, cId) for sql in (csql, msql, fsql)]

def projectEnable(key, flag):
    sql = "update PROJECT set enabled = %s where id = %s"
    __templeExecute(sql, (flag, key))

def removeProject(key):
    sql = "delete from project where id = %s"
    __templeExecute(sql, (key,))

def __templeExecute(sql, param):
    conn   = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, param)
        conn.commit()
    except psycopg2.ProgrammingError as e:
        raise(e)
    finally:
        cursor.close()
        cursor.close()

def __templeSearchDetailed(sql, key):
    key = (key, )
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql, key)
    return list(cursor.fetchall())

def __templeSearch(sql, key, projectId):
    param = (key + '%',)
    if projectId:
        sql += ' AND p.id = %s'
        param += (projectId,)
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql, param)
    return list(cursor.fetchall())

class ProjectDB():
    def __init__(self, projectMateData):
        try:
            self.__createProject(projectMateData)
        except Exception as e:
            raise e

    def insertOneClass(self, mate):
        classData, methodsData, fieldsData = mate
        classId = self.__insertIntoClassItem(classData)
        for field in fieldsData:
            self.__insertIntoFieldItem(classId, field)
        for method in methodsData:
            self.__insertIntoMethodItem(classId, method)
        return classId

    def commit(self):
        sql = "UPDATE PROJECT SET ENABLED = 'true' WHERE ID = %s"
        self.__templeExecute(sql, (self.projectId, ))

    def rollback(self):
        if self.projectId:
            try:
                self.__templeExecute("DELETE FROM PROJECT WHERE ID = %s", (self.projectId, ))
            except Exception as e:
                print("Couldn't remove project(%d), please do it by you own." % self.projectId)
                raise(e)

    def rollbackOneClass(self, key):
        try:
            self.__templeExecute("DELETE FROM classitem WHERE ID = %s", (key, ))
        except Exception as e:
            print("Couldn't remove class(%d), please do it by you own." % self.projectId)

    def __templeExecute(self, sql, param, needReturn = False):
        conn   = getConnection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, param)
            conn.commit()
            if needReturn:
                return cursor.fetchall()
        except psycopg2.ProgrammingError as e:
            raise(e)
        finally:
            cursor.close()
            cursor.close()

    def __createProject(self, projectMateData):
        sql = ("INSERT INTO PROJECT(NAME, VERSION, ENABLED, LANGUAGE, ICONHREF) "
               "VALUES(%s, %s, %s, %s, %s) RETURNING ID")

        self.projectId = self.__templeExecute(sql, projectMateData, True)[0][0]

    def __insertIntoClassItem(self, classData):
        sql = ("INSERT INTO CLASSITEM(FULLNAME, SIMPLENAME, HREF, PROJECTID)"
               "VALUES(%s, %s, %s, %s) RETURNING ID")
        classData = classData + (self.projectId, )
        return self.__templeExecute(sql, classData, True)[0][0]

    def __insertIntoFieldItem(self, classId, fieldData):
        sql = ("INSERT INTO FIELDITEM(CLASSITEMID, FILEDNAME, HREF)"
                  "VALUES(%s, %s, %s)")
        fieldData = (classId, ) + fieldData
        self.__templeExecute(sql, fieldData)

    def __insertIntoMethodItem(self, classId, methodData):
        sql = ("INSERT INTO METHODITEM(CLASSITEMID, SIGNNAME, HREF, TYPE)"
                  "VALUES(%s, %s, %s, %s)")
        methodData = (classId, ) + methodData
        self.__templeExecute(sql, methodData)

if __name__ == "__main__":
    createTable()
