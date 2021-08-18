from logging import error
from zeep import Client, xsd, exceptions
import os
from loguru import logger
from datetime import datetime
from EformServiceException import EformServiceException

wsdlPath = os.path.abspath(os.path.dirname(__file__))
#client and service definition for Core Service
#Core services WSDL location
CORESERVICE_WSDL = os.path.join(wsdlPath, "wsdl_coreService/BNI_CoreService.wsdl")
client = Client(CORESERVICE_WSDL)
service = client.create_service('{http://service.bni.co.id/core/Binding2}WSExport_IFCoreServiceHttpBinding', os.getenv('ENV_CORESERVICE_ENDPOINT'))
coreServiceResponse = None
requestObject = client.get_type('ns0:Request') 

inputTellerId = {
        "branch" : '',
        "terminal" : "001",
        "teller" : "",
        "overrideFlag" : "I",
        "tandemFlag" : None,
        "supervisorId" : None,
        "systemJournal" : None
}

customHeader = {
        "branch" : '',
        "terminal" : "001",
        "teller" : "88",
        "overrideFlag" : "I",
        "tandemFlag" : None,
        "supervisorId" : None,
        "systemJournal" : None
}

def checkCifFromId(branch:str, idNum:str, tellerId:str):
    try:
        customHeader['branch'] = branch
        #get cif from Id
        objectType = client.get_type('ns1:CifDetailsReqId')
        cifDetailsReq = {
            "cifNum" : idNum
        }
        content = xsd.AnyObject(objectType, cifDetailsReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'API', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'API', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        cifDetailsRes = coreServiceResponse['content']
        
        return cifDetailsRes

    except exceptions.Fault as fault:
        
        if fault.detail != None:
            faultDetail = fault.detail
            faultObject = faultDetail[0]
            errorNum = faultObject[0].text
            errorDescription = faultObject[1].text
            print(faultObject.tag)
            logger.info('{0}|{1} Fault returned when calling Core Service (CifDetails). '.format(idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException(errorDescription, 'ICONS', errorNum, errorDescription)
        else:
            logger.info(fault)
            errorNum = '9081'
            errorDescription = 'GENERAL ERROR'
            logger.info('{0}|{1} Error occured when calling Core Service (CifDetails). '.format(idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')

def checkCifFromAccount(accountNum: str, branch: str, refNum:str, idNum:str, tellerId: str):
    try:
        customHeader['branch'] = branch
        #get cif from account
        objectType = client.get_type('ns1:CifDetailsReq')
        cifDetailsReq = {
            "cifNum" : accountNum
        }
        content = xsd.AnyObject(objectType, cifDetailsReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'API', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'API', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        cifDetailsRes = coreServiceResponse['content']
        
        return cifDetailsRes
        
    except exceptions.Fault as fault:
        
        if fault.detail != None:
            faultDetail = fault.detail
            faultObject = faultDetail[0]
            errorNum = faultObject[0].text
            errorDescription = faultObject[1].text
            print(faultObject.tag)
            logger.info('{0}|{1} Fault returned when calling Core Service (CifDetails). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException(errorDescription, 'ICONS', errorNum, errorDescription)
        else:
            logger.info(fault)
            errorNum = '9081'
            errorDescription = 'GENERAL ERROR'
            logger.info('{0}|{1} Error occured when calling Core Service (CifDetails). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')

def openNewAccount(cifNum: str, branch: str, accountType: str, subCat: str, openAccReason:str, othersOpenAccReason:str, srcOfFund:str, 
othersSrcOfFund:str, sourceAccount:str, projDep:str,refNum:str, idNum:str, tellerId:str) :
    try:
        #create rekening based on cif
        customHeader['branch'] = branch
        objectType = client.get_type('ns1:InitCreateDEPAccountReq')
        initCreateDEPAccountReq = {
            "cif_or_accntNumber" : cifNum
        }
        content = xsd.AnyObject(objectType, initCreateDEPAccountReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'API', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'API', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        initCreateDEPAccountRes = coreServiceResponse['content']
        objectType = client.get_type('ns1:CreateDepositAccountReq')
        createDepositAccountReq = initCreateDEPAccountRes
        createDepositAccountReq['accountType'] = accountType
        createDepositAccountReq['subCategory'] = subCat
        createDepositAccountReq['openAccReason'] = openAccReason
        createDepositAccountReq['othersOpenAccReason'] = othersOpenAccReason
        createDepositAccountReq['srcOfFund'] = srcOfFund
        createDepositAccountReq['othersSrcOfFund'] = othersSrcOfFund
        createDepositAccountReq['sourceAccount'] = sourceAccount
        createDepositAccountReq['projDep'] = projDep
        createDepositAccountReq['branchId'] = branch
        for x in createDepositAccountReq:
            if createDepositAccountReq[x] != None and type(createDepositAccountReq[x]) == str:
                createDepositAccountReq[x] = createDepositAccountReq[x].strip()
        content = xsd.AnyObject(objectType, createDepositAccountReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'API', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'API', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        okMessage = coreServiceResponse['content']
        message = okMessage['message'].strip()
        splitMessage = message.split(' ')
        splitRekening = splitMessage[9].split('-')
        newAccountNum = splitRekening[0] + splitRekening[1]
        return newAccountNum.strip()
    except exceptions.Fault as fault:
        
        if fault.detail != None:
            faultDetail = fault.detail
            faultObject = faultDetail[0]
            errorNum = faultObject[0].text
            errorDescription = faultObject[1].text
            print(faultObject.tag)
            logger.info('{0}|{1} Fault returned when calling Core Service (InitCreateDepositAccount or CreateDEPAccount). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException(errorDescription, 'ICONS', errorNum, errorDescription)
        else:
            logger.info(fault)
            errorNum = '9081'
            errorDescription = 'GENERAL ERROR'
            logger.info('{0}|{1} Error occured when calling Core Service (InitCreateDepositAccount or CreateDEPAccount). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')

def custTidakBekerja (cifNum: str, branch: str, pemberiDanaKerja: str, alamatPemberiKerja1:str, hubunganPemberiDana:str, pekerjaanPemberiDana:str, jabatanPemberiDana: str, kabKotaPemberiDana:str, hpNo1PemberiDana:str, hpNo2PemberiDana:str, kodePos: str, npwpPemberiDana:str, tipeIdPemberiDana:str, idPemberiDana:str, perumPemberiDana:str, rtPemberiDana: str, rwPemberiDana:str, provinsiPemberiDana:str, kecamatanPemberiDana:str, kelDesaPemberiDana: str, alamatLain:str, perumLain:str, rtLainPemberiDana:str, rwLainPemberiDana: str, provinsiLainPemberiDana:str, kabupatenLain:str, kecamatanLainPemberiDana:str, kelDesaLainPemberiDana: str, kodeposLain:str, tempatLahirPemberiDana:str,  statusKawinPemberiDana: str, wargaNegaraPemberiDana:str, jenisKelaminPemberiDana: str, tglLahirPemberiDana: str, alamatKerjaPemberiDana: str, komplekKerjaPemberiDana:str, rtKerjaPemberiDana:str, rwKerjaPemberiDana:str, provinsiKerjaPemberiDana: str, kabKerjaPemberiDana:str, kecamatanKerjaPemberiDana:str, kelDesaKerjaPemberiDana:str, kodeposKerjaPemberiDana: str, noTelp1KerjaPemberiDana:str, noTelp2KerjaPemberiDana:str, sumberDana:str, adaNPWP:str, pertahun:str, transaksiUsaha:str, refNum:str, idNum:str, tellerId:str) :
    try:
   
        customHeader['branch'] = branch
        objectType = client.get_type('ns1:InquiryCustJobDetailReq')
        inquiryCustJobDetailReq = {
            "cifNum" : cifNum
        }
        content = xsd.AnyObject(objectType, inquiryCustJobDetailReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'EFORM', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'EFORM', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        inquiryCustJobDetailRes = coreServiceResponse['content']
        objectType = client.get_type('ns1:UpdateBeneficiaryOwnerReq')
        updateBeneficiaryOwnerReq = inquiryCustJobDetailRes
        updateBeneficiaryOwnerReq['pemberiDanaKerja'] = pemberiDanaKerja
        updateBeneficiaryOwnerReq['alamatPemberiKerja1'] = alamatPemberiKerja1
        updateBeneficiaryOwnerReq['hubunganPemberiDana'] = hubunganPemberiDana
        updateBeneficiaryOwnerReq['pekerjaanPemberiDana'] = pekerjaanPemberiDana
        updateBeneficiaryOwnerReq['jabatanPemberiDana'] = jabatanPemberiDana
        updateBeneficiaryOwnerReq['kabKotaPemberiDana'] = kabKotaPemberiDana
        updateBeneficiaryOwnerReq['hpNo1PemberiDana'] = hpNo1PemberiDana
        updateBeneficiaryOwnerReq['hpNo2PemberiDana'] = hpNo2PemberiDana
        updateBeneficiaryOwnerReq['kodePos'] = kodePos
        updateBeneficiaryOwnerReq['npwpPemberiDana'] = npwpPemberiDana
        updateBeneficiaryOwnerReq['tipeIdPemberiDana'] = tipeIdPemberiDana
        updateBeneficiaryOwnerReq['idPemberiDana'] = idPemberiDana
        updateBeneficiaryOwnerReq['perumPemberiDana'] = perumPemberiDana
        updateBeneficiaryOwnerReq['rtPemberiDana'] = rtPemberiDana
        updateBeneficiaryOwnerReq['rwPemberiDana'] = rwPemberiDana
        updateBeneficiaryOwnerReq['provinsiPemberiDana'] = provinsiPemberiDana
        updateBeneficiaryOwnerReq['kecamatanPemberiDana'] = kecamatanPemberiDana
        updateBeneficiaryOwnerReq['kelDesaPemberiDana'] = kelDesaPemberiDana
        updateBeneficiaryOwnerReq['alamatLain'] = alamatLain
        updateBeneficiaryOwnerReq['perumLain'] = perumLain
        updateBeneficiaryOwnerReq['rtLainPemberiDana'] = rtLainPemberiDana
        updateBeneficiaryOwnerReq['rwLainPemberiDana'] = rwLainPemberiDana
        updateBeneficiaryOwnerReq['provinsiLainPemberiDana'] = provinsiLainPemberiDana
        updateBeneficiaryOwnerReq['kabupatenLain'] = kabupatenLain
        updateBeneficiaryOwnerReq['kecamatanLainPemberiDana'] = kecamatanLainPemberiDana
        updateBeneficiaryOwnerReq['kelDesaLainPemberiDana'] = kelDesaLainPemberiDana
        updateBeneficiaryOwnerReq['kodeposLain'] = kodeposLain
        updateBeneficiaryOwnerReq['tempatLahirPemberiDana'] = tempatLahirPemberiDana
        updateBeneficiaryOwnerReq['statusKawinPemberiDana'] = statusKawinPemberiDana
        updateBeneficiaryOwnerReq['wargaNegaraPemberiDana'] = wargaNegaraPemberiDana
        updateBeneficiaryOwnerReq['jenisKelaminPemberiDana'] = jenisKelaminPemberiDana
        updateBeneficiaryOwnerReq['tglLahirPemberiDana'] = tglLahirPemberiDana
        updateBeneficiaryOwnerReq['alamatKerjaPemberiDana'] = alamatKerjaPemberiDana
        updateBeneficiaryOwnerReq['komplekKerjaPemberiDana'] = komplekKerjaPemberiDana
        updateBeneficiaryOwnerReq['rtKerjaPemberiDana'] = rtKerjaPemberiDana
        updateBeneficiaryOwnerReq['rwKerjaPemberiDana'] = rwKerjaPemberiDana
        updateBeneficiaryOwnerReq['provinsiKerjaPemberiDana'] = provinsiKerjaPemberiDana
        updateBeneficiaryOwnerReq['kabKerjaPemberiDana'] = kabKerjaPemberiDana
        updateBeneficiaryOwnerReq['kecamatanKerjaPemberiDana'] = kecamatanKerjaPemberiDana
        updateBeneficiaryOwnerReq['kelDesaKerjaPemberiDana'] = kelDesaKerjaPemberiDana
        updateBeneficiaryOwnerReq['kodeposKerjaPemberiDana'] = kodeposKerjaPemberiDana
        updateBeneficiaryOwnerReq['noTelp1KerjaPemberiDana'] = noTelp1KerjaPemberiDana
        updateBeneficiaryOwnerReq['noTelp2KerjaPemberiDana'] = noTelp2KerjaPemberiDana
        updateBeneficiaryOwnerReq['sumberDana'] = sumberDana 
        updateBeneficiaryOwnerReq['adaNPWP'] = adaNPWP
        updateBeneficiaryOwnerReq['pertahun'] = pertahun
        updateBeneficiaryOwnerReq['transaksiUsaha'] = transaksiUsaha
        for x in updateBeneficiaryOwnerReq:
            if updateBeneficiaryOwnerReq[x] != None and type(updateBeneficiaryOwnerReq[x]) == str:
                updateBeneficiaryOwnerReq[x] = updateBeneficiaryOwnerReq[x].strip()
        content = xsd.AnyObject(objectType, updateBeneficiaryOwnerReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'EFORM', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'EFORM', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        okMessage = coreServiceResponse['content']
        message = okMessage['message'].strip()
        return message
    except exceptions.Fault as fault:
        
        if fault.detail != None:
            faultDetail = fault.detail
            faultObject = faultDetail[0]
            errorNum = faultObject[0].text
            errorDescription = faultObject[1].text
            print(faultObject.tag)
            logger.info('{0}|{1} Fault returned when calling Core Service (UpdateBeneficiaryOwner). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException(errorDescription, 'ICONS', errorNum, errorDescription)
        else:
            logger.info(fault)
            errorNum = '9081'
            errorDescription = 'GENERAL ERROR'
            logger.info('{0}|{1} Error occured when calling Core Service (UpdateBeneficiaryOwner). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')
            
            
def custBekerja(cifNum: str, branch: str, detailPekerjaan: str, namaTempatKerja: str, alamatTempatKerja:str, alamatTempatKerja2:str, kodePos:str, tanggalMulaiKerja:str,refNum:str, idNum:str, tellerId:str) :
    try:

        customHeader['branch'] = branch
        objectType = client.get_type('ns1:InquiryCustJobDetailReq')
        inquiryCustJobDetailReq = {
            "cifNum" : cifNum
        }
        content = xsd.AnyObject(objectType, inquiryCustJobDetailReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'EFORM', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'EFORM', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        inquiryCustJobDetailRes = coreServiceResponse['content']
        objectType = client.get_type('ns1:UpdateCustJobDetailsReq')
        updateCustJobDetailsReq = inquiryCustJobDetailRes
        updateCustJobDetailsReq['keteranganJabatan'] = detailPekerjaan
        updateCustJobDetailsReq['pemberiDanaKerja'] = namaTempatKerja
        updateCustJobDetailsReq['alamatPemberiKerja1'] = alamatTempatKerja
        updateCustJobDetailsReq['alamatPemberiKerja2'] = alamatTempatKerja2
        updateCustJobDetailsReq['kodePos'] = kodePos
        updateCustJobDetailsReq['tanggalMulaiKerja'] = tanggalMulaiKerja
        for x in updateCustJobDetailsReq:
            if updateCustJobDetailsReq[x] != None and type(updateCustJobDetailsReq[x]) == str:
                updateCustJobDetailsReq[x] = updateCustJobDetailsReq[x].strip()
        content = xsd.AnyObject(objectType, updateCustJobDetailsReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'EFORM', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'EFORM', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        okMessage = coreServiceResponse['content']
        message = okMessage['message'].strip()
        return message
    except exceptions.Fault as fault:
        
        if fault.detail != None:
            faultDetail = fault.detail
            faultObject = faultDetail[0]
            errorNum = faultObject[0].text
            errorDescription = faultObject[1].text
            print(faultObject.tag)
            logger.info('{0}|{1} Fault returned when calling Core Service (UpdateBeneficiaryOwner). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException(errorDescription, 'ICONS', errorNum, errorDescription)
        else:
            logger.info(fault)
            errorNum = '9081'
            errorDescription = 'GENERAL ERROR'
            logger.info('{0}|{1} Error occured when calling Core Service (UpdateBeneficiaryOwner). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')
            
            
def openNewCif(req, branch: str, refNum:str, idNum:str, tellerId:str) :
    cifNum = ''
    try:
        customHeader['branch'] = branch
        idNum = req.idNum
        custName = req.customerName.strip()
        splitCustName = custName.split(' ')
        numOfTokens = len(splitCustName)
        firstName = ''
        middleName = ''
        if numOfTokens == 1 :
            lastName = splitCustName[0]
        elif numOfTokens >= 2 :
            lastName = splitCustName[-1]
            splitCustName.pop(-1)
            numOfTokens = numOfTokens - 1
            if len(lastName) < 3 :
                lastName = splitCustName[-1] + ' ' + lastName
                splitCustName.pop(-1)
                numOfTokens = numOfTokens - 1
            if numOfTokens > 0 :
                firstName = splitCustName[0]
                numOfTokens = numOfTokens - 1
                splitCustName.pop(0)
                for x in splitCustName:
                    middleName = middleName.strip() + ' ' + x
                

        else:
            raise Exception("Customer name not valid")
        print('First Name: ' + firstName)
        print('Middle Name: ' + middleName)
        print('Last Name: ' + lastName)

        rt = req.rt
        if len(rt) < 3 :
            padLength = 3 - len(rt)
            for x in range(padLength):
                rt = '0' + rt
        rw = req.rw
        if len(rw) < 3 :
            padLength = 3 - len(rw)
            for x in range(padLength):
                rw = '0' + rw
        
        homePhone = req.homePhone
        if len(homePhone) > 5:
            homePhoneNum1 = homePhone[0:4]
            homePhoneNum2 = homePhone[4:]
        else :
            homePhoneNum1 = ''
            homePhoneNum2 = ''
        
        mobileNum = req.mobileNum
        if len(mobileNum) > 5:
            handPhone1 = mobileNum[0:4]
            handPhone2 = mobileNum[4:]
        else :
            handPhone1 = ''
            handPhone2 = ''

        #fix no telp kantor tidak muncul di bancslink
        officeNum = req.officePhone
        if len(officeNum) > 5:
            officePhone1 = officeNum[0:4]
            officePhone2 = officeNum[4:]
        else :
            officePhone1 = ''
            officePhone2 = ''
        #end fix no telp kantor

        if len(req.taxId.strip()) >= 15:
            optNpwp = '1'
        else :
            optNpwp = '0'

        dob = datetime.strptime(req.dateOfBirth,'%Y-%m-%d')
        dob_core = dob.strftime('%d%m%Y')

        createCifReq = {
            'cifNum' : '',
            'customerType' : '01',
            'title' : '99',
            'relManager' : '',
            'firstName' : firstName,
            'lastName' : lastName,
            'gelar' : '',
            'companyName' : '',
            'legalEntity' : '',
            'adrress1' : req.customerAddress.strip(),
            'address2' : rt + rw,
            'address3' : req.kelurahan,
            'address4' : req.kecamatan,
            'zipCode' : req.postalCode,
            'countryCode' : 'ID',
            'homePhone1' : homePhoneNum1,
            'homePhone2' : homePhoneNum2,
            'noFax1' : '',
            'noFax2' : '',
            'officePhone1' : officePhone1, #fix no telp kantor tdk muncul
            'officePhone2' : officePhone2, #fix no telp kantor tdk muncul
            'handPhone1' : handPhone1,
            'handPhone2' : handPhone2,
            'nationality' : 'ID',
            'occupant' : '',
            'languageCode' : '',
            'idNumber' : req.idNum.strip(),
            'publisherCity' : req.publisherCity,
            'idType' : req.idType.strip(),
            'jobCode' : req.job.strip(),
            'BISegmentCode' : '3100',
            'optNPWP' : optNpwp,
            'branchOpening' : branch,
            'BIOwnerCode' : '9000',
            'companyGroup' : '9999',
            'middleName' : middleName,
            'locationCode' : '0391',
            'bebasPph' : 'Y',
            'idDueDate' : '31122099',
            'placeOfBirth' : req.pob,
            'dateOfBirth' : dob_core,
            'gender' : req.gender,
            'isMaried' : req.isMaried,
            'motherName' : req.motherMaidenName,
            'income' : req.yearlyIncome.strip(),
            'frekuensi' : 'M',
            'religion' : req.religion,
            'education' : req.education.strip(),
            'email' : req.email.strip(),
            'NPWPNum' : req.taxId.strip(),
            'status' : '000'
        }
        objectType = client.get_type('ns1:CreateCIFReq')
        content = xsd.AnyObject(objectType, createCifReq)
        if tellerId == None or tellerId == '':
            request = requestObject(customHeader = customHeader,systemId = 'API', content = content)
        else:
            inputTellerId['branch'] = branch
            inputTellerId['teller'] = tellerId
            request = requestObject(customHeader = inputTellerId,systemId = 'API', content = content)
        with client.settings(strict = False):
            coreServiceResponse = service.transaction(request = request)
        createCIFRes = coreServiceResponse['content']
        message = createCIFRes['message'].strip()
        splitMessage = message.split(' ')
        splitCif = splitMessage[8].split('-')
        cifNum = splitCif[0] + splitCif[1]
        return cifNum.strip()
    except exceptions.Fault as fault:
        if fault.detail != None:
            faultDetail = fault.detail
            faultObject = faultDetail[0]
            errorNum = faultObject[0].text
            errorDescription = faultObject[1].text
            if errorNum == '3656' or 'CIF=' in errorDescription :
                errorDescSplit = errorDescription.split(' ')
                cifNum = errorDescSplit[6]
                cifNum = cifNum[1:]
                logger.info('{0}|{1} ID Number already have CIF. Returning existing CIF num: '.format(refNum, idNum) + cifNum)
            else:
                logger.info('{0}|{1} Fault returned when calling Core Service (CreateCIF). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
                raise EformServiceException(errorDescription, 'ICONS', errorNum, errorDescription)
        else:
            logger.info(fault)
            errorNum = '9081'
            errorDescription = 'GENERAL ERROR'
            logger.info('{0}|{1} Error occured when calling Core Service (CreateCIF). '.format(refNum, idNum) + errorNum + ' ' + errorDescription)
            raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')
    return cifNum