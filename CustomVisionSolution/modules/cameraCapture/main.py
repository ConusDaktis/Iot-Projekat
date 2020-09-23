import time
import sys
import os
import requests
import json

import iothub_client
from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

MESSAGE_TIMEOUT = 10000

# Biramo MQTT kao transport protokol.  
PROTOCOL = IoTHubTransportProvider.MQTT

SEND_CALLBACKS = 0

# Slanje poruke na IoT Hub
# output1 saljemo na $upstream u deployment.template.json
def send_to_hub(strMessage):
    message = IoTHubMessage(bytearray(strMessage, 'utf8'))
    hubManager.send_event_to_output("output1", message, 0)

# Callback dobijen kada je poruka poslata na IoT Hub procesirana.
def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    SEND_CALLBACKS += 1
    print ( "Confirmation received for message with result = %s" % result )
    print ( "   Total calls confirmed: %d \n" % SEND_CALLBACKS )

# slanje slike na image classifying server
# Vraca JSON response sa servera sa rezultatom predikcije
def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
    headers = {'Content-Type': 'application/octet-stream'}

    with open(imagePath, mode="rb") as test_image:
        try:
            response = requests.post(imageProcessingEndpoint, headers = headers, data = test_image)
            print("Response from classification service: (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
        except Exception as e:
            print(e)
            print("Response from classification service: (" + str(response.status_code))

    return json.dumps(response.json())

class HubManager(object):
    def __init__(self, protocol, message_timeout):
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        # postavljanje vremena do timeout-a
        self.client.set_option("messageTimeout", message_timeout)

    # Slanje poruke na output. 
    def send_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(
            outputQueueName, event, send_confirmation_callback, send_context)

def main(imagePath, imageProcessingEndpoint):
    try:
        print ( "Simulated camera module for Azure IoT Edge. Press Ctrl-C to exit." )

        try:
            global hubManager 
            hubManager = HubManager(PROTOCOL, MESSAGE_TIMEOUT)
        except IoTHubError as iothub_error:
            print ( "Unexpected error %s from IoTHub" % iothub_error )
            return

        print ( "The sample is now sending images for processing and will indefinitely.")

        videostream = False
        print('this is the imagePath: ', imagePath)
        if imagePath=='picamera':
            videostream = True
            imagePath = '/camframes/frame.jpg'
            res = (640,480)
            import picamera
            print('picamera imported successfully')
            camera = picamera.PiCamera()
            print('picamera object created')
            camera.resolution = res
            camera.framerate = 24
            time.sleep(5)
            print('video stream')

        while True:
            if videostream:
                camera.capture(imagePath)
            classification = sendFrameForProcessing(imagePath, imageProcessingEndpoint)
            send_to_hub(classification)
            time.sleep(10)

    except KeyboardInterrupt:
        print ( "IoT Edge module sample stopped" )

if __name__ == '__main__':
    try:
        IMAGE_PATH = os.getenv('IMAGE_PATH', "")
        IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "")
    except ValueError as error:
        print ( error )
        sys.exit(1)

    if ((IMAGE_PATH and IMAGE_PROCESSING_ENDPOINT) != ""):
        main(IMAGE_PATH, IMAGE_PROCESSING_ENDPOINT)
    else: 
        print ( "Error: Image path or image-processing endpoint missing" )