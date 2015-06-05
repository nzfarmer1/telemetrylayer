# import topicmanagers.digisense
import os


def classFactory(iface):
    from tank.agtank import agTankTopicManager
    from relay.agrelay import agRelayTopicManager

    return [{"name": "AgSense Tank", "class": agTankTopicManager(iface)},
            {"name": "AgSense Relay", "class": agRelayTopicManager(iface)}]

