
def setup(serverId):
    from sessions.server.replication import factory, replicator
    factory.setup(serverId)
    replicator.setup()
