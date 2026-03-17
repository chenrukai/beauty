package com.beauty.knowledge.common.constant;

public interface RabbitMQConstant {

    String PROCESS_EXCHANGE = "knowledge.process.exchange";
    String PROCESS_DLX = "knowledge.process.dlx";
    String PROCESS_QUEUE = "knowledge.process.queue";
    String PROCESS_DLQ = "knowledge.process.dlq";
    String PROCESS_ROUTING_KEY = "knowledge.process";
    // Keep consistent with existing broker queue arguments to avoid PRECONDITION_FAILED.
    String DLQ_ROUTING_KEY = "knowledge.process.dlq.routing.key";
}
