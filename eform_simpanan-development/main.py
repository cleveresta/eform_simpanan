from datetime import datetime
import uvicorn
from fastapi import FastAPI
import logging
import os
import platform
from zeep import Client, xsd, exceptions, helpers
from zeep.xsd.types.builtins import String
from pathlib import Path
import zlib

import dbAccess
from CheckAccountRequest import CheckAccountRequest
from CheckAccountResponse import CheckAccountResponse
from CreateAccountRequest import CreateAccountRequest
from CreateAccountResponse import CreateAccountResponse
from EformServiceException import EformServiceException
from custom_logging import CustomizeLogger
from ConfigLoader import ConfigLoader
import BlinkServiceHandler
import CoreServiceHandler
import FaceRecognition
from loguru import logger

config_path=Path(__file__).with_name("logging_config.json")

def create_app() -> FastAPI:
    #app = FastAPI(title='e-Form Simpanan Service', debug=False, docs_url= None, redoc_url = None)
    app = FastAPI(title='e-Form Simpanan Service', debug=True) #for dev only
    logger_server = CustomizeLogger.make_logger(config_path)
    app.logger = logger_server

    return app

app = create_app()

tags_metadata = [
    {
        "name": "simpanan",
        "description": "Pembukaan rekening simpanan dengan verifikasi data kependudukan secara otomatis",
    },
    {
        "name": "checkaccountbranchless",
        "description": "Cek apakah NIK sudah pernah buka via e-channel",
    }
]

name = str(platform.node())
pid = str(os.getpid())
logId = name + " - " + pid
sourceAccount = '999999999999999999' #untuk pembukaan via eChannel
wsdlPath = os.path.abspath(os.path.dirname(__file__))


#client and service definition for OTP Service
#OTP services WSDL location
OTP_WSDL = os.path.join(wsdlPath, "wsdl_otp/BP_OTPEngine_OTPExport.wsdl")
otpClient = Client(OTP_WSDL)
otpService = otpClient.create_service('{http://service.bni.co.id/otp}OTPExport_IFOtpHttpBinding', os.getenv('ENV_OTP_ENDPOINT'))
otpServiceResponse = None

#client and service definition for SMS Sender Service
#SMS sender services WSDL location
SMSSENDER_WSDL = os.path.join(wsdlPath, "wsdl_smsSender/SB_SMSBanking_SMSSender_WSExport.wsdl")
smsSenderClient = Client(SMSSENDER_WSDL)
smsSenderService = smsSenderClient.create_service('{http://service.bni.co.id/smssender/Binding}SMSSender_WSExport_IFSMSSenderHttpBinding', os.getenv('ENV_SMSSENDER_ENDPOINT'))

appConfig = ConfigLoader()

@app.post('/eform/simpanan', response_model=CreateAccountResponse, response_model_exclude_unset=True, tags=["simpanan"])
async def create_account(req: CreateAccountRequest):
    startDate = datetime.now()
    refNum = req.refNum
    tellerId = req.tellerId
    accountNum = req.accountNum
    channel = req.channel.strip()
    branch = req.branch.strip()
    accountType = req.accountType.strip()
    subCat = req.subCat.strip()
    openAccReason = req.openAccReason.strip()
    srcOfFund = req.srcOfFund.strip()
    othersOpenAccReason = req.othersOpenAccReason.strip()
    othersSrcOfFund = req.othersSrcOfFund.strip()
    projDep = req.projDep.strip()
    otp = req.otp.strip()
    address = req.customerAddress.strip()
    cifNum = ''
    newAccountNum = ''
    status = ''
    errorCode = ''
    errorDescString = ''
    custName = req.customerName.strip()
    idNum = req.idNum.strip()
    idType = req.idType.strip()
    mobileNum = req.mobileNum.strip()
    homePhone = ''
    isDukcapilOk = False
    isOtpValid = False
    detailPekerjaan = req.detailPekerjaan.strip()
    namaTempatKerja = req.namaTempatKerja.strip()
    alamatTempatKerja = req.alamatTempatKerja.strip()
    alamatTempatKerja2 = req.alamatTempatKerja2.strip()
    kodePos = req.kodePos.strip()
    tanggalMulaiKerja = req.startWorkDate.strip()
    updateBeneficiaryOwner = ''
    pekerjaan = req.job.strip()
    channelPromoCode = req.channelPromotionCode
    numOfOtpTries = 3
    pemberiDanaKerja = req.patronName.strip()
    alamatPemberiKerja1 = req.patronAddress.strip()
    hubunganPemberiDana = req.patronRelationship.strip()
    pekerjaanPemberiDana = req.patronJob.strip()
    jabatanPemberiDana = req.patronJobTitle.strip()
    kabKotaPemberiDana = req.patronCity.strip()
    hpNo1PemberiDana = req.patronMobileNum.strip()
    npwpPemberiDana = req.patronTaxId.strip()
    tipeIdPemberiDana = req.patronIdType.strip()
    idPemberiDana = req.patronIdNum.strip()
    perumPemberiDana = req.patronBuilding.strip()
    rtPemberiDana = req.patronRt.strip()
    rwPemberiDana = req.patronRw.strip()
    provinsiPemberiDana = req.patronProvince.strip()
    kecamatanPemberiDana = req.patronKec.strip()
    kelDesaPemberiDana = req.patronKel.strip()
    alamatLain = req.alamatLain.strip()
    perumLain = req.perumLain.strip()
    rtLainPemberiDana = req.rtLainPemberiDana.strip()
    rwLainPemberiDana = req.rwLainPemberiDana.strip()
    provinsiLainPemberiDana = req.provinsiLainPemberiDana.strip()
    kabupatenLain = req.kabupatenLain.strip()
    kecamatanLainPemberiDana = req.kecamatanLainPemberiDana.strip()
    kelDesaLainPemberiDana = req.kelDesaLainPemberiDana.strip()
    kodeposLain = req.kodeposLain.strip()
    tempatLahirPemberiDana = req.patronPob.strip()
    statusKawinPemberiDana = req.patronMarriageStatus.strip()
    wargaNegaraPemberiDana = req.patronNationality.strip()
    jenisKelaminPemberiDana = req.jenisKelaminPemberiDana.strip()
    tglLahirPemberiDana = req.tglLahirPemberiDana.strip()
    alamatKerjaPemberiDana = req.patronCompanyAddress.strip()
    komplekKerjaPemberiDana = req.komplekKerjaPemberiDana.strip()
    rtKerjaPemberiDana = req.rtKerjaPemberiDana.strip()
    rwKerjaPemberiDana = req.rwKerjaPemberiDana.strip()
    provinsiKerjaPemberiDana = req.provinsiKerjaPemberiDana.strip()
    kabKerjaPemberiDana = req.kabKerjaPemberiDana.strip()
    kecamatanKerjaPemberiDana = req.kecamatanKerjaPemberiDana.strip()
    kelDesaKerjaPemberiDana = req.kelDesaKerjaPemberiDana.strip()
    kodeposKerjaPemberiDana = req.kodeposKerjaPemberiDana.strip()
    noTelp1KerjaPemberiDana = req.patronCompanyPhone.strip()
    noTelp2KerjaPemberiDana = req.noTelp2KerjaPemberiDana.strip()
    sumberDana = req.patronSrcOfFund.strip()
    adaNPWP = req.adaNPWP.strip()
    pertahun = req.patronYearlyIncome.strip()
    transaksiUsaha = req.patronOpenAccReason.strip()
    hpNo1PemberiDana = req.patronMobileNum.strip()
    nomor = ''

    result = {
        "accountNum" : accountNum,
        "channel": channel,
        "branch": branch,
        "customerName" : custName,
        "idNum" : idNum,
        "idType" : idType
    }
    

    otpRequestObject = otpClient.get_type('ns0:OtpRequest')
    otpValueObject = otpClient.get_type('ns0:OtpValue')

    try:
        #TODO
        #validasi input. id_num, id_type, customerName, mobilenum
        #sanity check, required input should be exist
        nomor = hpNo1PemberiDana
        if len(nomor) > 4:
            hpNo1PemberiDana = nomor[0:3]
            hpNo2PemberiDana = nomor[4:]
        else :
            hpNo1PemberiDana = ''
            hpNo2PemberiDana = ''
             
        if idNum == None or idNum == '' or idType == None or idType == '':
            #throw Exception
            logger.info('{0}|{1} Invalid idNum and/or idType'.format(refNum, idNum))
            errorCode = '9009'
            errorDescString = 'INVALID INPUT SPECIFIED'
            raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)

        cifDetailsRes = CoreServiceHandler.checkCifFromAccount(accountNum, branch, refNum, idNum, tellerId)
        cifNum = cifDetailsRes['cifNum']

        if cifNum != None and cifNum != '':
            #throw Exception
            logger.info('{0}|{1} Invalid idNum'.format(refNum, idNum))
            errorCode = '9009'
            errorDescString = 'NIK SUDAH MEMILIKI CIF'
            raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)

        if mobileNum == None or mobileNum == '' :
            #throw Exception
            logger.info('{0}|{1} Invalid mobile phone number'.format(refNum, idNum))
            errorCode = '9009'
            errorDescString = 'INVALID INPUT SPECIFIED'
            raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)

        if custName == None or custName == '' :
            #throw Exception
            logger.info('{0}|{1} Invalid customer name'.format(refNum, idNum))
            errorCode = '9009'
            errorDescString = 'INVALID INPUT SPECIFIED'
            raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
        
        if refNum == None or refNum == '':
            try:
                dateNowString = startDate.strftime('%Y-%m-%d')
                otpWaitingAccount = dbAccess.getAccountByIdTime(idNum, idType, channel, 'OTP_WAIT%', dateNowString + ' 00:00:00', dateNowString + ' 23:59:59')
            except Exception as e:
                logger.info('{0}|{1} Error happened when getting data from db'.format(idNum, idType))
                print(e)
                errorCode = '9002'
                errorDescString = 'PROCESS FAILED, DATABASE PROBLEM'
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)

            dateTimeString = startDate.strftime('%Y%m%dT%H%M%S.%f')
            refNumString = dateTimeString + 'ID' + idNum + 'HP' + mobileNum
            refNumByte = refNumString.encode('utf-8')
            refNum = channel[0:4] + str(zlib.adler32(refNumByte))

            if otp == None or otp != 'otp_req' :
               #throw Exception
                logger.info('{0}|{1} Empty reference number only for otp request'.format(refNum, idNum))
                errorCode = '9009'
                errorDescString = 'INVALID INPUT SPECIFIED'
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)

            if otpWaitingAccount != None:
                numOfEntries = len(otpWaitingAccount)
                if numOfEntries >= 3:
                    logger.info('{0}|{1} Too many OTP request from channel: {2}'.format(refNum, idNum, channel))
                    errorCode = '9001'
                    errorDescString = 'TOO MANY OTP REQUEST ATTEMPTS'
                    raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
            
            status = 'OTP_WAIT1'
        else:
            refNum = refNum.strip()
            try:
                account = dbAccess.selectByRefNumHPID(refNum.strip(), idNum, idType, mobileNum, channel)
            except Exception as e:
                logger.info('{0}|{1} Error happened when getting data from db'.format(idNum, idType))
                print(e)
                errorCode = '9002'
                errorDescString = 'PROCESS FAILED, DATABASE PROBLEM'
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
            
            
            if account == None or len(account) == 0:
                logger.info('{0}|{1} No data with refNum: {2}'.format(refNum, idNum, refNum))
                errorCode = '9005'
                errorDescString = 'INVALID REFERENCE NUMBER'
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
            else:
                statusInDb = account[69]
                lastStatusChar = statusInDb[-1]
                logger.info('{0}|{1} Reference status in db: {2}'.format(refNum, idNum, account[69]))
                if 'OTP_WAIT' in statusInDb:
                    lastStatusCount = int(lastStatusChar)
                    if otp == 'otp_req' :
                        status = 'OTP_WAIT' + str(lastStatusCount + 1)
                    
                    if lastStatusCount > numOfOtpTries: 
                        logger.info('{0}|{1} Too many OTP requests from: {2}'.format(refNum, idNum, channel))
                        status = 'OTP_BLOCK'
                        errorCode = '9001'
                        errorDescString = 'TOO MANY OTP REQUEST ATTEMPTS'
                        raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
                elif 'OTP_FAIL' in statusInDb:
                    lastStatusCount = int(lastStatusChar)
                    if otp == 'otp_req' :
                        status = 'OTP_WAIT' + str(lastStatusCount + 1)
                    else:
                        status = 'OTP_FAIL' + str(lastStatusCount + 1)
                    if lastStatusCount > numOfOtpTries: 
                        logger.info('{0}|{1} Too many OTP failure from: {2}'.format(refNum, idNum, channel))
                        status = 'OTP_BLOCK'
                        errorCode = '9011'
                        errorDescString = 'TOO MANY OTP FAILURES'
                        raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
                else:
                    logger.info('{0}|{1} This reference number already blocked/succeeded opened account. Please start over {2}'.format(refNum, idNum, channel))
                    errorCode = '9010'
                    errorDescString = 'REFERENCE NUMBER CAN NOT BE USED ANYMORE'
                    raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)

        if otp.lower() == 'otp_req':
            logger.info('{0}|{1} Request and send OTP to customer'.format(refNum, idNum))
            #request + send sms
            otpRequest = otpRequestObject(applicationId = 'EFORMDN', channelId = 'EFORM', keyValue = mobileNum)
            try:
                with otpClient.settings(strict = False):
                    otpResult = otpService.request(otpRequest = otpRequest)
                dateTimeNowString = startDate.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                smsConfig = appConfig.getConfig('smsSenderParameters')
                headerOutSmsSender = {
                    'smsProviderId' : smsConfig.get('provider'),
                    'method' : smsConfig.get('method'),
                    'transactionType' : smsConfig.get('transactionType'),
                    'msisdn' : mobileNum,
                    'transactionId' : '',
                    'transactionDate' : dateTimeNowString
                }
                #BNI : Kode OTP Anda untuk Layanan Pembukaan Rekening Digital adalah xxxxxx (rahasia). Kode ini berlaku selama 3 menit. Info lebih lanjut hubungi 1500046
                message = 'BNI : Kode OTP Anda untuk Layanan Pembukaan Rekening Digital adalah ' + otpResult + ' (rahasia). Kode ini berlaku selama 3 menit. Info lebih lanjut hubungi 1500046'
                logger.info('{0}|{1} SMS Content: '.format(refNum, idNum) + message)
                with smsSenderClient.settings(strict = False, raw_response = True): #raw_response set to True coz WS doesn't return anything
                    smsSenderService.sendMessage(headerOut = headerOutSmsSender, message = message)
                logger.info('{0}|{1} OTP sent to customer'.format(refNum, idNum))
            except Exception as e:
                logger.info('{0}|{1} Error happened when generating/sending OTP'.format(refNum, idNum))
                print(e)
                errorCode = '9003'
                errorDescString = 'FAILED TO GENERATE OTP'
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
        else :
            #verify + use otp
            try:
                openedAccount = dbAccess.getAccountById(idNum, idType, channel, 'SUCCESS')
            except Exception as e:
                logger.info('{0}|{1} Error happened when getting data from db'.format(idNum, idType))
                print(e)
                errorCode = '9002'
                errorDescString = '(SOA) PROCESS FAILED, DATABASE PROBLEM'
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)

            otpValue = otpValueObject(applicationId = 'EFORMDN', channelId = 'EFORM', keyValue = mobileNum, otpResult = otp)
            try:
                with otpClient.settings(strict = False):
                    isOtpValid = otpService.validate(otpValue = otpValue)
                if isOtpValid :
                    logger.info('{0}|{1} OTP Valid. Continue process'.format(refNum, idNum))
                    with otpClient.settings(strict = False, raw_response = True):
                        otpService.use(otpValue = otpValue)
                else :
                    lastStatusChar = statusInDb[-1]
                    if int(lastStatusChar) >= numOfOtpTries: 
                        logger.info('{0}|{1} Too many OTP failure from: {2}'.format(refNum, idNum, channel))
                        status = 'OTP_BLOCK'
                        errorCode = '9011'
                        errorDescString = 'TOO MANY OTP FAILURES'
                        raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
                    else:
                        status = 'OTP_FAIL' + str(int(lastStatusChar))
                        logger.info('{0}|{1} OTP is not valid'.format(refNum, idNum))
                        raise EformServiceException(errorDescString, 'SOA', '9004', 'FAILED TO VALIDATE OTP')
            except Exception as e:
                logger.info('{0}|{1} Error happened when validating OTP'.format(refNum, idNum))
                print(e)
                errorCode = '9004'
                errorDescString = 'FAILED TO VALIDATE OTP'
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
            
            if openedAccount != None:
                logger.info('{0}|{1} This ID have opened account via {2}'.format(refNum, idNum, channel))
                errorCode = '9008'
                errorDescString = 'ID HAS OPENED ACCOUNT VIA {0}'.format(channel)
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
            #TODO
            #Validasi NIK pakai Face Recognition
            logger.info('{0}|{1} ID Number validation (for KTP with face recognition)'.format(refNum, idNum))
            frServiceResponse = FaceRecognition.recogniseFaceAndData(custName, req.dateOfBirth, req.pob, req.selfiePhoto, '', refNum, idNum)
            print(frServiceResponse)
            if frServiceResponse['name'] == 'true' :
                isNameOk = True
            else :
                isNameOk = False
            if frServiceResponse['birthdate'] == 'true' :
                isDobOk = True
            else :
                isDobOk = False
            if frServiceResponse['birthplace'] == 'true' :
                isPobOk = True
            else :
                isPobOk = False
            selfiePhotoPercent = float(frServiceResponse['selfiePhoto'])
            #frAddress = frServiceResponse['address']
            selfiePhotoReferencePercent = float(appConfig.getConfig('photoThreshold'))
            if not (isNameOk and isDobOk and isPobOk and selfiePhotoPercent > selfiePhotoReferencePercent):
                logger.info('{0}|{1} ID Number validation (for KTP with face recognition) not OK'.format(refNum, idNum))
                errorCode = '9006'
                errorDescString = 'FAILED TO VALIDATE IDENTITY'
                raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
            logger.info('{0}|{1} ID Number validation (for KTP with face recognition) done'.format(refNum, idNum))

            if accountNum is not None and accountNum != '':
                logger.info('{0}|{1} Existing customer. accountNum: '.format(refNum, idNum) + accountNum + '. Check for account\'s CIF')
                cifDetailsRes = CoreServiceHandler.checkCifFromAccount(accountNum, branch, refNum, idNum, tellerId)
                cifNum = cifDetailsRes['cifNum']
                if cifDetailsRes['firstName'] != None and type(cifDetailsRes['firstName']) == str:
                    firstName = cifDetailsRes['firstName'].strip()
                else:
                    firstName = ''
                if cifDetailsRes['middleName'] != None and type(cifDetailsRes['middleName']) == str:
                    middleName = cifDetailsRes['middleName'].strip()
                else:
                    middleName = ''
                if cifDetailsRes['lastName'] != None and type(cifDetailsRes['lastName']) == str:
                    lastName = cifDetailsRes['lastName'].strip()
                else:
                    lastName = ''
                custName = firstName + ' ' + middleName + ' ' + lastName
                address = cifDetailsRes['jalan']
                logger.info('{0}|{1} Got the CIF. CIF number: '.format(refNum, idNum) + cifNum)
            else :
                logger.info('{0}|{1} New customer or existing account number is blank. Create new CIF '.format(refNum, idNum))
                cifNum = CoreServiceHandler.openNewCif(req, branch, refNum, idType, tellerId)
                logger.info('{0}|{1} Create new CIF or get the existing one OK. CIF number: '.format(refNum, idNum) + cifNum)
            if pekerjaan == '08' or pekerjaan == '09' or pekerjaan == '10' :
                updateBeneficiaryOwner = CoreServiceHandler.custTidakBekerja(cifNum, branch, pemberiDanaKerja, alamatPemberiKerja1, hubunganPemberiDana, pekerjaanPemberiDana, jabatanPemberiDana, kabKotaPemberiDana, hpNo1PemberiDana, hpNo2PemberiDana, kodePos, npwpPemberiDana, tipeIdPemberiDana, idPemberiDana, perumPemberiDana, rtPemberiDana, rwPemberiDana, provinsiPemberiDana, kecamatanPemberiDana, kelDesaPemberiDana, alamatLain, perumLain, rtLainPemberiDana, rwLainPemberiDana, provinsiLainPemberiDana, kabupatenLain, kecamatanLainPemberiDana, kelDesaLainPemberiDana, kodeposLain, tempatLahirPemberiDana, statusKawinPemberiDana, wargaNegaraPemberiDana, jenisKelaminPemberiDana, tglLahirPemberiDana, alamatKerjaPemberiDana, komplekKerjaPemberiDana, rtKerjaPemberiDana, rwKerjaPemberiDana, provinsiKerjaPemberiDana, kabKerjaPemberiDana, kecamatanKerjaPemberiDana, kelDesaKerjaPemberiDana, kodeposKerjaPemberiDana, noTelp1KerjaPemberiDana, noTelp2KerjaPemberiDana, sumberDana, adaNPWP, pertahun, transaksiUsaha, refNum, idNum, tellerId)
            else :
                updateBeneficiaryOwner = CoreServiceHandler.custBekerja(cifNum, branch, detailPekerjaan, namaTempatKerja, alamatTempatKerja, alamatTempatKerja2, kodePos, tanggalMulaiKerja, refNum, idNum, tellerId)
            logger.info('{0}|{1} Create account with that CIF'.format(refNum, idNum))
            newAccountNum = CoreServiceHandler.openNewAccount(cifNum, branch, accountType, subCat, openAccReason, othersOpenAccReason, srcOfFund, 
                            othersSrcOfFund, sourceAccount, projDep, refNum,idNum, tellerId)
            result['newAccountNum'] = newAccountNum
            status = 'SUCCESS'
            errorCode = ''
            errorDescString = ''
            logger.info('{0}|{1} New account successfully created. Account num: '.format(refNum, idNum) + newAccountNum)
    except EformServiceException as eformException:
        if status == None or status == '' :
            status = 'FAILED'
        errorCode = eformException.errorCode
        errorDescString = '(' + eformException.origin + ') ' + eformException.errorMessage
        logger.info('{0}|{1} An error has occured. '.format(refNum, idNum) + ' ' + errorCode + ' ' + errorDescString)

    try:
        if req.refNum == None or req.refNum == '': 
            dbAccess.insertAccount(startDate, vars(req), refNum, newAccountNum, cifNum, custName[0:99],idNum,idType,channel, homePhone, mobileNum, address[0:99],status, errorCode, errorDescString[0:99], '')
        else:
            if errorDescString is not None and len(errorDescString) > 100:
                errorDescString = errorDescString[0:98]
            dbAccess.updateAccount(refNum, newAccountNum, cifNum, idNum,idType,mobileNum, status, errorCode, errorDescString)
    except Exception as error:
        logger.info('{0}|{1} Failed to insert account information. Database problem'.format(refNum, idNum))
        logger.info(error)
        errorCode = '9002'
        errorDescString = '(SOA) PROCESS ' + status + ', DATABASE PROBLEM'
        status = 'FAILED'
       
    result['cifNum'] = cifNum
    result['status'] = status
    result['refNum'] = refNum
    result['errorCode'] = errorCode
    result['errorMessage'] = errorDescString
    endDate = datetime.now()
    timeDelta = endDate - startDate
    logger.info('{0}|{1} Process finished. Time elapsed: '.format(refNum, idNum) + str(timeDelta.total_seconds()*1000) + 'ms')
    return result

@app.post('/eform/ceknikbranchless', response_model=CheckAccountResponse, response_model_exclude_unset=True, tags=["checkaccountbranchless"])
async def create_account(req: CheckAccountRequest):
    startDate = datetime.now()
    channel = req.channel.strip()
    idNum = req.idNum.strip()
    idType = req.idType.strip()
    result = {
        "channel": channel,
        "idNum" : idNum,
        "idType" : idType
    }
    errorCode = ''
    errorDescString = ''
    status = 'SUCCESS'
    try:
        try:
            openedAccount = dbAccess.getAccountById(idNum, idType, channel, 'SUCCESS')
        except Exception as e:
            logger.info('{0}|{1} Error happened when getting data from db'.format(idNum, idType))
            print(e)
            errorCode = '9002'
            errorDescString = '(SOA) PROCESS FAILED, DATABASE PROBLEM'
            raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
        if openedAccount != None:
            logger.info('{0}|{1} This ID have opened account via {2}'.format(idNum, idType, channel))
            errorCode = '9008'
            errorDescString = 'ID HAS OPENED ACCOUNT VIA {0}'.format(channel)
            raise EformServiceException(errorDescString, 'SOA', errorCode, errorDescString)
    except EformServiceException as eformException:
        status = 'FAILED'
        errorCode = eformException.errorCode
        errorDescString = '(' + eformException.origin + ') ' + eformException.errorMessage
        logger.info('{0}|{1} An error has occured. '.format(idNum, idType) + ' ' + errorCode + ' ' + errorDescString)
    
    result['status'] = status
    result['errorCode'] = errorCode
    result['errorMessage'] = errorDescString

    endDate = datetime.now()
    timeDelta = endDate - startDate
    logger.info('{0}|{1} Process finished. Time elapsed: '.format(idNum, idType) + str(timeDelta.total_seconds()*1000) + 'ms')
    return result
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9090)