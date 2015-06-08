# import topicmanagers.digisense
import os


def classFactory():
    from tank.agtank import agTankTopicManager
    from relay.agrelay import agRelayTopicManager
    from text.agtext import agTextTopicManager

    return [{"name": "Tank", "class": agTankTopicManager()},
            {"name": "Text", "class": agTextTopicManager()},
            {"name": "Relay", "class": agRelayTopicManager()}]

