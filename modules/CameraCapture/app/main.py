#!/usr/bin/env python

import sys
import os
import json
import picamera
import requests
import io

# import local devicecheck module
import hubmanager
import iothub_client
# pylint: disable=E0611
# Disabling linting that is not supported by Pylint for C extensions such as iothub_client. See issue https://github.com/PyCQA/pylint/issues/1955
from iothub_client import (IoTHubModuleClient, IoTHubClientError, IoTHubError,
                           IoTHubMessage, IoTHubMessageDispositionResult,
                           IoTHubTransportProvider)

hub = None
IMAGE_CLASSIFY_THRESHOLD = .5
MESSAGE_TIMEOUT = 10000

# global counters
SEND_CALLBACKS = 0


def send_to_Hub_callback(strMessage):
    message = IoTHubMessage(bytearray(strMessage, 'utf8'))
    hubManager.send_event_to_output("output1", message, 0)

# Callback received when the message that we're forwarding is processed.


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    SEND_CALLBACKS += 1


class HubManager(object):

    def __init__(self, connection_string = None, protocol = IoTHubTransportProvider.MQTT):
        if not connection_string:
            connection_string = os.environ['EdgeHubConnectionString']

        print("\nPython %s\n" % sys.version)
        print("IoT Hub Client for Python")
        print("Starting the IoT Hub Python sample using protocol %s..." % protocol)

        self.client_protocol = protocol
        self.client = IoTHubClient(connection_string, protocol)

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)
        # some embedded platforms need certificate information
        self.set_certificates()

    def set_certificates(self):
        CERT_FILE = os.environ['EdgeModuleCACertificateFile']
        print("Adding TrustedCerts from: {0}".format(CERT_FILE))

        # this brings in x509 privateKey and certificate
        with open(CERT_FILE) as file:
            try:
                self.client.set_option("TrustedCerts", file.read())
                print("set_option TrustedCerts successful")
            except IoTHubClientError as iothub_client_error:
                print("set_option TrustedCerts failed (%s)" % iothub_client_error)
				
	
	def send_event_to_output(self, outputQueueName, event, send_context):
		self.client.send_event_async(
			outputQueueName, event, send_confirmation_callback, send_context)


# Pull camera images and stream data to image classifier module.
def stream_camera_data(camera):
    while True:
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg')
        stream.seek(0)
        image = {'image': stream}

        try:
            requests.post('http://image-classifier:8080/classify', files=image, hooks={'response': c_request_response})
        except Exception as e:
            print(e)


# Image classifier module callback.
def c_request_response(r, *args, **kwargs):
    results = json.loads(r.content)
    label = results[0]['label']
    probability = results[0]['score']
    print('Label: {}, Probability: {:.2f}'.format(label, probability))

    # Send the prediction to IoT Edge.
    message = IoTHubMessage(r.content)
    hub.client.send_event_async(
        "predictions", message, send_confirmation_callback, results)


def send_confirmation_callback(message, result, user_context):
    print("Confirmation received with result: {} message: {}\n".format(result, user_context))


# device_twin_callback is invoked when twin's desired properties are updated.
def device_twin_callback(update_state, payload, user_context):
    global IMAGE_CLASSIFY_THRESHOLD

    print("\nTwin callback called with:\nupdateStatus = {}\npayload = {}".format(update_state, payload))
    data = json.loads(payload)
    if "desired" in data:
        data = data["desired"]

    if "ImageClassifyThreshold" in data:
        IMAGE_CLASSIFY_THRESHOLD = float(data["ImageClassifyThreshold"])


if __name__ == '__main__':

    # Create the IoT Edge connection.
    hub = hubmanager.HubManager()
    hub.client.set_device_twin_callback(device_twin_callback, 0)

    # Create the camera object and start camera stream.
    camera = picamera.PiCamera()
    stream_camera_data(camera)
