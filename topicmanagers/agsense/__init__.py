# import topicmanagers.digisense
import os


def classFactory(iface):
    from agtopicmanager import agTopicManager

    return {"name": "AgSense", "class": agTopicManager}

