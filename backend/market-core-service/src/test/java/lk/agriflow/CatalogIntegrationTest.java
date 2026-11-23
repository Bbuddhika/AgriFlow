package lk.agriflow;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.RabbitMQContainer;
import org.springframework.amqp.core.AmqpAdmin;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessageBuilder;
import org.springframework.amqp.core.MessageDeliveryMode;
import org.springframework.amqp.rabbit.connection.CorrelationData;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import lk.agriflow.config.MessagingConfiguration;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.hasSize;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class CatalogIntegrationTest {
    @Container
    static final PostgreSQLContainer<?> DATABASE = new PostgreSQLContainer<>("postgres:17-alpine");

    @Container
    static final RabbitMQContainer BROKER = new RabbitMQContainer("rabbitmq:4-management-alpine");

    @DynamicPropertySource
    static void database(DynamicPropertyRegistry properties) {
        properties.add("spring.datasource.url", DATABASE::getJdbcUrl);
        properties.add("spring.datasource.username", DATABASE::getUsername);
        properties.add("spring.datasource.password", DATABASE::getPassword);
        properties.add("spring.rabbitmq.host", BROKER::getHost);
        properties.add("spring.rabbitmq.port", BROKER::getAmqpPort);
        properties.add("spring.rabbitmq.username", BROKER::getAdminUsername);
        properties.add("spring.rabbitmq.password", BROKER::getAdminPassword);
        properties.add("spring.rabbitmq.virtual-host", () -> "/");
    }

    @Autowired MockMvc mvc;
    @Autowired AmqpAdmin amqp;
    @Autowired RabbitTemplate rabbit;

    @Test
    void notificationQueuesAreDeclaredOnTheBroker() {
        assertNotNull(amqp.getQueueInfo(MessagingConfiguration.NOTIFICATIONS));
        assertNotNull(amqp.getQueueInfo(MessagingConfiguration.NOTIFICATIONS_DLQ));
    }

    @Test
    void confirmedMessagesRouteAndRejectedMessagesReachTheDeadLetterQueue() throws Exception {
        // Synthetic broker fixture only; this does not execute a business action.
        String id = UUID.randomUUID().toString();
        byte[] body = ("{\"probeId\":\"" + id + "\"}").getBytes(StandardCharsets.UTF_8);
        Message message = MessageBuilder.withBody(body)
            .setContentType("application/json")
            .setMessageId(id)
            .setDeliveryMode(MessageDeliveryMode.PERSISTENT)
            .build();
        CorrelationData confirmation = new CorrelationData(id);
        rabbit.send(MessagingConfiguration.EVENTS, "reservation.accepted.v1", message, confirmation);
        assertTrue(confirmation.getFuture().get(10, TimeUnit.SECONDS).isAck());
        assertNull(confirmation.getReturned());

        rabbit.execute(channel -> {
            var delivery = channel.basicGet(MessagingConfiguration.NOTIFICATIONS, false);
            assertNotNull(delivery);
            assertArrayEquals(body, delivery.getBody());
            channel.basicReject(delivery.getEnvelope().getDeliveryTag(), false);
            return null;
        });
        Message failed = rabbit.receive(MessagingConfiguration.NOTIFICATIONS_DLQ, 5000);
        assertNotNull(failed);
        assertArrayEquals(body, failed.getBody());
    }

    @Test
    void migrationsAndCatalogReadWorkAgainstPostgres() throws Exception {
        mvc.perform(get("/api/v1/catalog/produce"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(6)))
            .andExpect(jsonPath("$[0].code").value("CABBAGE"));
    }

    @Test
    void unknownProtectedResourcesAreNotPublic() throws Exception {
        mvc.perform(get("/api/v1/admin/users")).andExpect(status().isUnauthorized());
        mvc.perform(post("/api/v1/catalog/produce")).andExpect(status().isForbidden());
    }

    @Test
    void readinessIncludesDatabaseAndRabbitMq() throws Exception {
        mvc.perform(get("/actuator/health/readiness"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UP"));
    }
}
