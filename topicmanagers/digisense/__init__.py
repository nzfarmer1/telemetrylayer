#import topicmanagers.digisense
import os


def classFactory():
    from dstopicmanager import dsTopicManager
    print __file__
 #   print os.path.dirname(__file__)
    dstopicmanager.deviceTypesPath = os.path.join(os.path.dirname(__file__),"dsdevices.xml")
#    print dstopicmanager.deviceTypesPath
    return {"name":"DigiSense","class":dsTopicManager}

