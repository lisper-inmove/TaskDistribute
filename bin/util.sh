#!/bin/bash

# 项目名称
export APPNAME=TaskDistribute
# 是否开启终端显示日志
export LOGGER_ENABLE_CONSOLE=true
# 是否开启syslog日志
export LOGGER_ENABLE_SYSLOG=true
# syslog日志服务器地址
export LOGGER_SYSLOG_HOST=logger.server
# syslog日志服务端口
export LOGGER_SYSLOG_PORT=514
# syslog日志设备
export LOGGER_SYSLOG_FACILITY=local7
# MongoDB数据库ip
export MONGODB_SERVER_ADDRESS=127.0.0.1
# MongoDB数据库端口
export MONGODB_PORT=27018
export MONGODB_CLUSTER_NODES=localhost:37017,localhost:37018,localhost:37019
export MONGODB_CLUSTER_AUTH_DB=admin
export MONGODB_CLUSTER_USER=root
export MONGODB_CLUSTER_REPLICA_SET=myrs
# export R_ENABLE_REPLICA=true
# 服务启动环境
export RUNTIME_ENVIRONMENT=test

# APITABLE服务
export TOKEN=uskHYI63inkUx3wqOMcnb1A
export APITABLE_HOST=http://127.0.0.1
export APITABLE_PORT=8800

export MQ_TYPE=KAFKA
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
export REDIS_STARTUP_NODES=redis1,7001:redis2,7002:redis3,7003:redis4,7004:redis5,7005:redis6,7006
export REDIS_LOCK_CONFIG=127.0.0.1,6379
export KAFKA_HOST=127.0.0.1
export KAFKA_PORT=9192
export PULSAR_HOST=pulsar://127.0.0.1
export PULSAR_PORT=6650
export PULSAR_TOPIC_PREFIX=persistent://public/default/

export PYTHONPATH=`pwd`/src
export APPROOT=`pwd`/src

function get_available_port() {
    port=6003
    while true
    do
        declare -i flag
        flag=`lsof -i:$port | wc -l`
        if [ $((flag)) -eq 0 ];then
           break
        else
           ((port++))
        fi
    done
    echo $((port+0))
}
