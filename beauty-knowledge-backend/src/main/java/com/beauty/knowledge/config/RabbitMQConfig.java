package com.beauty.knowledge.config;

import com.beauty.knowledge.common.constant.RabbitMQConstant;
import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.HashMap;
import java.util.Map;

@Configuration
public class RabbitMQConfig {

    @Bean
    public DirectExchange processExchange() {
        return new DirectExchange(RabbitMQConstant.PROCESS_EXCHANGE, true, false);
    }

    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange(RabbitMQConstant.PROCESS_DLX, true, false);
    }

    @Bean
    public Queue processQueue() {
        Map<String, Object> args = new HashMap<>();
        args.put("x-dead-letter-exchange", RabbitMQConstant.PROCESS_DLX);
        args.put("x-dead-letter-routing-key", RabbitMQConstant.DLQ_ROUTING_KEY);
        args.put("x-message-ttl", 300000);
        return new Queue(RabbitMQConstant.PROCESS_QUEUE, true, false, false, args);
    }

    @Bean
    public Queue deadLetterQueue() {
        return new Queue(RabbitMQConstant.PROCESS_DLQ, true);
    }

    @Bean
    public Binding processBinding(Queue processQueue, DirectExchange processExchange) {
        return BindingBuilder.bind(processQueue).to(processExchange).with(RabbitMQConstant.PROCESS_ROUTING_KEY);
    }

    @Bean
    public Binding deadLetterBinding(Queue deadLetterQueue, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(deadLetterQueue).to(deadLetterExchange).with(RabbitMQConstant.DLQ_ROUTING_KEY);
    }

    @Bean
    public Jackson2JsonMessageConverter jackson2JsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory, Jackson2JsonMessageConverter converter) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(converter);
        template.setMandatory(true);
        return template;
    }
}
