
_class ={}

def getClass(broker):

    """
      To avoid recusive include definitions, instances of sub topic manager types
      are created dynamically via the topicmanager instance(<topicType>) method
      
      These classes should be stateless with regards the tLayer, but optionally stateful
      with regards the Broker instance.
    
    """

    from agtank import agRelayTopicManager
    
    if broker in _class and _class[broker] is not None:
        return _class[broker] # return valid instance
    
    _class[broker]  = agRelayTopicManager(broker) # create new singleton
    return _class[broker]

