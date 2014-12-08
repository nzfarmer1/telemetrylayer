# import topicmanagers.digisense
import os


def classFactory(iface):
    from dstopicmanager import dsTopicManager

    return {"name": "DigiSense", "class": dsTopicManager}

