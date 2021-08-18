from logging import error
from zeep import Client, xsd, exceptions
import os
from loguru import logger
from datetime import datetime
from EformServiceException import EformServiceException

#client and service definition for Verijelas Service
#Verijelas services WSDL location
wsdlPath = os.path.abspath(os.path.dirname(__file__))
VERIJELAS_WSDL = os.path.join(wsdlPath, "wsdl_verijelas/API_VeriJelas.wsdl")
frClient = Client(VERIJELAS_WSDL)
frService = frClient.create_service('{http://service.bni.co.id/verijelas}API_VeriJelasBinding', os.getenv('ENV_FR_ENDPOINT'))
frServiceResponse = None
frRequestObject = frClient.get_type('ns0:Request')

def recogniseFaceAndData(name: str, birthDate: str, birthPlace: str, selfiePhoto: str, identityPhoto: str, refNum: str, idNum: str):
    #meow
    dob = datetime.strptime(birthDate, '%Y-%m-%d')
    dobString = dob.strftime('%d-%m-%Y')
    frRequest = frRequestObject(nik = idNum, name= name, birthplace = birthPlace, birthdate = dobString, identityPhoto = identityPhoto, selfiePhoto = selfiePhoto)
    try:
        with frClient.settings(strict = False):
            frServiceResponse = frService.checkSelfie(request = frRequest)
    except Exception as e:
        print(e)
        logger.info('{0}|{1} An error has occured when verifying data with face recognition. '.format(refNum, idNum))
        raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')

    if frServiceResponse['status'] == '200':
        return frServiceResponse['data']
    else :
        logger.info('{0}|{1} An error has occured when verifying data with face recognition (status non HTTP 200).'.format(refNum, idNum))
        logger.info('{0}|{1} Response: '.format(refNum, idNum) + str(frServiceResponse))
        raise EformServiceException('ERROR WHEN VALIDATE IDENTITY', 'SOA', '9007', 'ERROR WHEN VALIDATE IDENTITY')
    