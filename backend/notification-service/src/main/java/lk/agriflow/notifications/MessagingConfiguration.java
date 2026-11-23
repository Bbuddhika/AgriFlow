package lk.agriflow.notifications;

import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Declarables;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MessagingConfiguration {
    public static final String EVENTS = "agriflow.events";
    public static final String DEAD_LETTERS = "agriflow.dead-letters";
    public static final String NOTIFICATIONS = "agriflow.notifications.v1";
    public static final String NOTIFICATIONS_DLQ = "agriflow.notifications.dlq.v1";

    @Bean
    Declarables notificationTopology() {
        TopicExchange events = new TopicExchange(EVENTS, true, false);
        TopicExchange deadLetters = new TopicExchange(DEAD_LETTERS, true, false);
        Queue notifications = QueueBuilder.durable(NOTIFICATIONS)
            .deadLetterExchange(DEAD_LETTERS)
            .deadLetterRoutingKey(NOTIFICATIONS_DLQ)
            .build();
        Queue failedNotifications = QueueBuilder.durable(NOTIFICATIONS_DLQ).build();
        return new Declarables(events, deadLetters, notifications, failedNotifications,
            BindingBuilder.bind(notifications).to(events).with("reservation.accepted.v1"),
            BindingBuilder.bind(notifications).to(events).with("reservation.expired.v1"),
            BindingBuilder.bind(notifications).to(events).with("visit.status-changed.v1"),
            BindingBuilder.bind(notifications).to(events).with("inspection.completed.v1"),
            BindingBuilder.bind(notifications).to(events).with("sale.confirmed.v1"),
            BindingBuilder.bind(failedNotifications).to(deadLetters).with(NOTIFICATIONS_DLQ));
    }
}
