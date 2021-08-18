import cx_Oracle
import os
from datetime import datetime

ip = os.getenv('ENV_DB_HOST') #ip localhost kalau via VPN
#ip = '192.168.143.93'
username = os.getenv('ENV_DB_USER')
password = os.getenv('ENV_DB_PASS')
sid = os.getenv('ENV_DB_SID')
port = os.getenv('ENV_DB_PORT')
encoding = 'UTF-8'
   

def connect():
    try:
        dsn = cx_Oracle.makedsn(ip, port, sid)
        connection = cx_Oracle.connect(
            username,
            password,
            dsn,
            encoding = encoding)
        
        return connection
    except:
        raise
    
def insertAccount(timestamp, reqData, refNum, accountNum, cif, customerName, idNum, idType, channel, homePhone,
    mobileNum, address, status, errorCode, errorMessage, flag):
    try:
        #import pdb;pdb.set_trace()
        connection = connect()
        cursor = connection.cursor()
        ts = datetime.now()
        if reqData['dateOfBirth'] == None or reqData['dateOfBirth'] == '':
            dob = None
        else:
            dob = datetime.strptime(reqData['dateOfBirth'],'%Y-%m-%d')
        
        if reqData['startWorkDate'] == None or reqData['startWorkDate'] == '':
            startWorkDate = None
        else:
            startWorkDate = datetime.strptime(reqData['startWorkDate'],'%Y-%m-%d')

        if reqData['patronDob'] == None or reqData['patronDob'] == '':
            patronDob = None
        else:
            patronDob = datetime.strptime(reqData['patronDob'],'%Y-%m-%d')

        statement = 'INSERT INTO BRANCHLESS_OPEN_ACCOUNTS(TIMESTAMP, ACCOUNTNUM,ACCOUNT_TYPE,SUBCAT, ACCOUNT_HOME_BRANCH,CIFNUM,ID_NUM,ID_TYPE, NATIONALITY,CUSTOMER_NAME,\
                    DOB,EMAIL,HOME_PHONE,MOBILENUM,EDUCATION,HOBBY,OPEN_ACC_REASON,SRC_OF_FUND,PROJECTED_TRX,NPWP_NUM,\
                    ADDRESS,RT,RW,KELURAHAN,KECAMATAN,CITY,PROVINCE,POSTAL_CODE,JOB,JOB_TITLE,\
                    YEARLY_INCOME,COMPANY_NAME,COMPANY_ADDRESS,COMPANY_ADDRESS2,OFFICE_POSTAL_CODE,START_WORK_DATE,OFFICE_PHONE,PATRON_NAME,PATRON_ID_TYPE, PATRON_ID_NUM,\
                    PATRON_NPWP_NUM,PATRON_ADDRESS,PATRON_RT,PATRON_RW,PATRON_BUILDING,PATRON_KEL,PATRON_KEC,PATRON_CITY,PATRON_PROVINCE,PATRON_SRC_OF_FUND,\
                    PATRON_YEARLY_INCOME,PATRON_OPEN_ACC_REASON,PATRON_JOB,PATRON_JOB_TITLE,PATRON_RELATIONSHIP,PATRON_POB,PATRON_DOB,PATRON_NATIONALITY,PATRON_MARRIAGE_STATUS,PATRON_COMPANY_NAME,\
                    PATRON_COMPANY_ADDRESS,PATRON_COMPANY_ADDRESS2,PATRON_OFFICE_POSTAL_CODE,PATRON_MOBILE_NUM,FLAG,CHANNEL,ID_PHOTO,CUST_PHOTO,CUST_WITH_ID_PHOTO,STATUS,\
                    ERRORCODE,ERRORMESSAGE,LAST_UPDATE, REFNUM, CHANNELPROMOCODE)\
                    VALUES(:t_val, :accountNum, :accountType, :subCat, :accountBranch, :cifNum, :idNum, :idType, :nationality, :customerName,\
                    :dob, :email, :homePhone, :mobileNum, :education,:hobby, :openAccReason, :srcOfFund, :projDep, :taxId, \
                    :address, :rt,:rw, :kelurahan, :kecamatan, :city, :province, :postalCode, :job, :jobTitle,\
                    :yearlyIncome, :companyName, :companyAddress, :companyAddress2, :officePostalCode, :startWorkDate,:officePhone, :patronName, :patronIdType, :patronIdNum,\
                    :patronTaxId, :patronAddress, :patronRt, :patronRw, :patronBuilding, :patronKel, :patronKec, :patronCity, :patronProvince, :patronSrcOfFund,\
                    :patronYearlyIncome, :patronOpenAccReason, :patronJob, :patronJobTitle, :patronRelationship, :patronPob, :patronDob, :patronNationality, :patronMarriageStatus, :patronCompany,\
                    :patronCompanyAddress, :patronCompanyAddress2, :patronCompanyPostalCode, :patronMobileNum, :flagParam, :channel, :idPhoto, :custPhoto, :custWithIdPhoto, :status, \
                    :errorCode, :errorMessage, :t_val, :refNum, :channelPromoCode)'
        cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
        cursor.execute(statement, {
            't_val':timestamp, 'accountNum' : accountNum, 'accountType' : reqData['accountType'], 'subCat' : reqData['subCat'], 'accountBranch' : reqData['branch'], 'cifNum' : cif,'idNum' : idNum, 'idType' : idType, 'nationality' : '','customerName' : customerName,
            'dob' : dob, 'email' : reqData['email'], 'homePhone' : homePhone, 'mobileNum' : mobileNum, 'education' : reqData['education'],'hobby' : reqData['hobby'], 'openAccReason' : reqData['openAccReason'], 'srcOfFund' : reqData['srcOfFund'],'projDep' : reqData['projDep'],'taxId' : reqData['taxId'],
            'address': address, 'rt' : reqData['rt'],'rw' : reqData['rw'], 'kelurahan' : reqData['kelurahan'], 'kecamatan' : reqData['kecamatan'], 'city' : reqData['city'], 'province' : reqData['province'],'postalCode' : reqData['postalCode'], 'job' : reqData['job'],'jobTitle' : reqData['jobTitle'],
            'yearlyIncome' : reqData['yearlyIncome'], 'companyName' : reqData['companyName'], 'companyAddress' : reqData['companyAddress'], 'companyAddress2' : reqData['companyAddress2'], 'officePostalCode' : reqData['officePostalCode'],'startWorkDate' : startWorkDate,'officePhone' : reqData['officePhone'],'patronName' : reqData['patronName'],'patronIdType' : reqData['patronIdType'],'patronIdNum' : reqData['patronIdNum'],
            'patronTaxId' : reqData['patronTaxId'], 'patronAddress' : reqData['patronAddress'],'patronRt' : reqData['patronRt'],'patronRw' : reqData['patronRw'],'patronBuilding' : reqData['patronBuilding'],'patronKel' : reqData['patronKel'],'patronKec' : reqData['patronKec'],'patronCity' : reqData['patronCity'], 'patronProvince' : reqData['patronProvince'],'patronSrcOfFund' : reqData['patronSrcOfFund'],
            'patronYearlyIncome' : reqData['patronYearlyIncome'], 'patronOpenAccReason' : reqData['patronOpenAccReason'],'patronJob' : reqData['patronJob'],'patronJobTitle' : reqData['patronJobTitle'],'patronRelationship' : reqData['patronRelationship'],'patronPob' : reqData['patronPob'],'patronDob' : patronDob, 'patronNationality' : reqData['patronNationality'], 'patronMarriageStatus' : reqData['patronMarriageStatus'],'patronCompany' : reqData['patronCompany'],
            'patronCompanyAddress' : reqData['patronCompanyAddress'],'patronCompanyAddress2' : reqData['patronCompanyAddress2'],'patronCompanyPostalCode' : reqData['patronCompanyPostalCode'], 'patronMobileNum' : reqData['patronMobileNum'],
            'flagParam' : flag,'channel' : channel, 'idPhoto' : '','custPhoto' : '','custWithIdPhoto' : '','status' : status, 'errorCode' : errorCode, 'errorMessage' : errorMessage, 'refNum' : refNum, 'channelPromoCode' : reqData['channelPromotionCode']
            })
        commit(cursor) 
    except:
        raise

def updateAccount(refNum, accountNum, cif, idNum, idType, mobileNum, status, errorCode, errorMessage):
    try:
        #import pdb;pdb.set_trace()
        connection = connect()
        cursor = connection.cursor()
        ts = datetime.now()
        statement = 'UPDATE BRANCHLESS_OPEN_ACCOUNTS SET \
                    ACCOUNTNUM = :accountNum,\
                    CIFNUM = :cifNum,\
                    STATUS = :status,\
                    ERRORCODE = :errorCode,\
                    ERRORMESSAGE = :errorMessage,\
                    LAST_UPDATE = :t_val\
                    WHERE ID_NUM = :idNum AND ID_TYPE = :idType AND REFNUM = :refNum AND MOBILENUM = :mobileNum '
                    # 
        cursor.execute(statement, {
            't_val':ts, 'accountNum' : accountNum,  'cifNum' : cif, 
            'status' : status, 'errorCode' : errorCode, 'errorMessage' : errorMessage, 
            'mobileNum' : mobileNum,
            'idNum' : idNum, 
            'idType' : idType,         
            'refNum' : refNum
            })
        commit(cursor) 
    except:

        raise

def selectByRefNum(refNum):
    try:
        #import pdb;pdb.set_trace()
        connection = connect()
        with connection.cursor() as cursor:
            statement = 'SELECT * FROM BRANCHLESS_OPEN_ACCOUNTS \
                        WHERE REFNUM = :refNum'
            cur = cursor.execute(statement, {         
                'refNum' : refNum
                })
            cur.fetchmany()
            for x in cur:
                print(x)
    except:
        
        raise
def selectByRefNumHPID(refNum,idNum, idType, mobileNum, channel):
    try:
        #import pdb;pdb.set_trace()
        connection = connect()
        with connection.cursor() as cursor:
            statement = 'SELECT * FROM BRANCHLESS_OPEN_ACCOUNTS \
                        WHERE ID_NUM = :idNum AND ID_TYPE = :idType \
                        AND REFNUM = :refNum AND MOBILENUM = :mobileNum \
                        AND CHANNEL = :channel'
            cur = cursor.execute(statement, {         
                'mobileNum' : mobileNum,
                'idNum' : idNum, 
                'idType' : idType,         
                'refNum' : refNum,
                'channel' : channel
                })
            rows = cur.fetchmany()
            if not rows:
                return None
            else:
                return rows[0]
    except:
        
        raise

def getAccountById(idNum, idType, channel, status):
    try:
        connection = connect()
        with connection.cursor() as cursor:
            statement = 'SELECT * FROM BRANCHLESS_OPEN_ACCOUNTS \
                        WHERE ID_NUM = :idNum AND ID_TYPE = :idType AND CHANNEL = :channel AND STATUS = :status'
            cur = cursor.execute(statement, {         
                'idNum' : idNum, 
                'idType' : idType, 
                'channel' : channel,        
                'status' : status
                })
            rows = cur.fetchmany()
            if not rows:
                return None
            else:
                return rows
    except:
        
        raise

def getAccountByIdTime(idNum, idType, channel, status, timeStart, timeEnd):
    try:
        connection = connect()
        if timeStart == None or timeStart == '':
            timeStartParam = None
        else:
            timeStartParam = datetime.strptime(timeStart,'%Y-%m-%d %H:%M:%S')
        if timeEnd == None or timeEnd == '':
            timeEndParam = None
        else:
            timeEndParam = datetime.strptime(timeEnd,'%Y-%m-%d %H:%M:%S')
        with connection.cursor() as cursor:
            statement = 'SELECT * FROM BRANCHLESS_OPEN_ACCOUNTS \
                        WHERE ID_NUM = :idNum AND ID_TYPE = :idType \
                        AND CHANNEL = :channel AND STATUS LIKE :status \
                        AND TIMESTAMP BETWEEN :startDate AND :endDate'
            cur = cursor.execute(statement, {         
                'idNum' : idNum, 
                'idType' : idType, 
                'channel' : channel,        
                'status' : status,
                'startDate' : timeStartParam,
                'endDate' : timeEndParam
                })
            rows = cur.fetchmany()
            if not rows:
                return None
            else:
                return rows
    except:
        
        raise

def closeConnection(cursor):
    connection = cursor.connection
    if(cursor):
        cursor.close()
    
    if(connection):
        connection.close()

def commit(cursor):
    connection = cursor.connection
    if(connection):
        connection.commit()
    closeConnection(cursor)
