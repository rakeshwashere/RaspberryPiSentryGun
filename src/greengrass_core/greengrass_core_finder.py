import os
import sys
import time
import uuid
import json
import logging

from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException
# from iot_core.constants import IoTCoreConstants


# Configure logging
logger = logging.getLogger("GreengrassCoreFinder")
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


class GreengrassCoreFinder:
    def __init__(self, endpoint, root_ca_path, certificate_path, private_key_path, thing_name):
        self.__certificate_path = certificate_path
        self.__private_key_path = private_key_path
        self.__thing_name = thing_name

        # Discover GGCs
        discoveryInfoProvider = DiscoveryInfoProvider()
        discoveryInfoProvider.configureEndpoint(endpoint)
        discoveryInfoProvider.configureCredentials(
            root_ca_path, certificate_path, private_key_path)
        discoveryInfoProvider.configureTimeout(10)  # 10 sec
        self.__discoveryInfoProvider = discoveryInfoProvider

    def __get_core_ca_from_aws(self):
        GROUP_CA_PATH = "./groupCA/"
        # Progressive back off core
        backoff_core = ProgressiveBackOffCore()

        MAX_DISCOVERY_RETRIES = 10
        retryCount = MAX_DISCOVERY_RETRIES
        while retryCount != 0:
            try:
                discoveryInfo = self.__discoveryInfoProvider.discover(
                    self.__thing_name)
                caList = discoveryInfo.getAllCas()
                coreList = discoveryInfo.getAllCores()

                # TODO handle cases where thing belongs to multiple Greengrass groups
                # We only pick the first ca and core info, a thing could ofcourse belong to multiple Greengrass core groups
                # but we'll handle that later (aka never)
                groupId, ca = caList[0]
                coreInfo = coreList[0]
                logger.info("Discovered GGC: %s from Group: %s" %
                      (coreInfo.coreThingArn, groupId))

                print("Now we persist the connectivity/identity information...")
                groupCA = GROUP_CA_PATH + groupId + \
                    "_CA_" + str(uuid.uuid4()) + ".crt"
                if not os.path.exists(GROUP_CA_PATH):
                    os.makedirs(GROUP_CA_PATH)
                groupCAFile = open(groupCA, "w")
                groupCAFile.write(ca)
                groupCAFile.close()

                discovered = True
                logger.info("Now proceed to the connecting flow...")
                break
            except DiscoveryInvalidRequestException as e:
                # TODO cleanup code duplication
                logger.error("Invalid discovery request detected!")
                logger.error("Type: %s" % str(type(e)))
                logger.error("Error message: %s" % e.message)
                logger.error("Stopping...")
                break
            except BaseException as e:
                logger.error("Error in discovery!")
                logger.error("Error message: %s", str(e))
                retryCount -= 1
                logger.info("\n%d/%d retries left\n" %
                      (retryCount, MAX_DISCOVERY_RETRIES))
                logger.info("Backing off...\n")
                backoff_core.backOff()

        if not discovered:
            logger.fatal("Discovery failed after %d retries. Exiting...\n" %
                         (MAX_DISCOVERY_RETRIES))
            sys.exit(-1)

        return groupCA, coreInfo

    def find_greengrass_core(self):
        groupCA, coreInfo = self.__get_core_ca_from_aws()
        # Iterate through all connection options for the core and use the first successful one
        greengrass_core_mqtt_client = AWSIoTMQTTClient(self.__thing_name)
        greengrass_core_mqtt_client.configureCredentials(
            groupCA, self.__private_key_path, self.__certificate_path)
        # myAWSIoTMQTTClient.onMessage = customOnMessage

        connected = False
        for connectivityInfo in coreInfo.connectivityInfoList:
            currentHost = connectivityInfo.host
            currentPort = connectivityInfo.port
            logger.info("Trying to connect to core at %s:%d" %
                  (currentHost, currentPort))
            greengrass_core_mqtt_client.configureEndpoint(currentHost, currentPort)
            try:
                greengrass_core_mqtt_client.connect()
                connected = True
                logger.info("Connected successfully to greengrass core locally %s:%d" % (
                    currentHost, currentPort))
                self.greengrass_core_mqtt_client = greengrass_core_mqtt_client
                return (currentHost, currentPort)
            except BaseException as e:
                logger.error("Error in connect!")
                logger.error("Error message: %s", str(e))

        if not connected:
            logger.fatal("Cannot connect to core %s. Exiting..." %
                  coreInfo.coreThingArn)
            sys.exit(-2)
        return 
    
    def get_core_mqtt_client(self):
        return self.greengrass_core_mqtt_client

