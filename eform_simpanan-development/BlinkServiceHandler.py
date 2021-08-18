from logging import error
from zeep import Client, xsd, exceptions
import os
from loguru import logger
from EformServiceException import EformServiceException

#client and service definition for Blink Service
#Blink services WSDL location
wsdlPath = os.path.abspath(os.path.dirname(__file__))
BLINK_WSDL = os.path.join(wsdlPath, "wsdl_blink/BancslinkExport.wsdl")
blinkClient = Client(BLINK_WSDL)
blinkService = blinkClient.create_service('{http://service.bni.co.id/bancslink}BancslinkTransactionHttpBinding', os.getenv('ENV_CHANNELSERVICE_ENDPOINT'))
blinkServiceResponse = None
blinkRequestObject = blinkClient.get_type('ns0:Request') 

def validateNikDukcapil(idNum: str, idType: str, refNum: str):
    #cek data ke dukcapil (tanpa face recognition)
    if idType == '0001' :
        blinkHeader = {
            'systemId' : 'DUKCAPIL',
            'branch'   : '0996',
            'terminal' : '001',
            'teller'   : '00001',
            'tranCode' : '96866'
        }
        contentTX096866 = {
            'nik' : idNum,
            'channel': 'EFORM'
        }
        blinkObjectType = blinkClient.get_type('ns1:TX096866')
        blinkContent = xsd.AnyObject(blinkObjectType, contentTX096866)
        blinkRequest = blinkRequestObject(Header = blinkHeader, Body = blinkContent)
        try:
            with blinkClient.settings(strict = False):
                blinkServiceResponse = blinkService.transaction(request = blinkRequest)
        except:
            logger.info('{0}|{1} An error has occured when getting data from Dukcapil. '.format(refNum, idNum))
            raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')

        blinkResponseBody = blinkServiceResponse[0]
        blinkStatusBody = blinkResponseBody['Body']
        if 'message' in blinkStatusBody :
            blinkResponseBody = blinkServiceResponse[1]
            return blinkResponseBody['Body']
        else :
            errorCode = 'DUKCAPIL' + blinkStatusBody['errorCode']
            errorDescString = blinkStatusBody['errorMessage']
            logger.info('{0}|{1} Received error from Dukcapil '.format(refNum, idNum) + errorCode + ' ' + errorDescString)
            raise EformServiceException(errorDescString, 'DUKCAPIL', errorCode, errorDescString)
        
    else:
        logger.info('{0}|{1} ID Type is not supported. '.format(refNum, idNum))
        raise EformServiceException('GENERAL ERROR', 'SOA', '9081', 'GENERAL ERROR')