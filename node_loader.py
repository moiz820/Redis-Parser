# nodes.yaml - Configuration for Redis distributed setup
nodes:
  - name: redis-master
    ip: 10.0.0.1
    port: 6379
    role: master

  - name: redis-replica-1
    ip: 10.0.0.2
    port: 6379
    role: replica

  - name: redis-replica-2
    ip: 10.0.0.3
    port: 6379
    role: replica
