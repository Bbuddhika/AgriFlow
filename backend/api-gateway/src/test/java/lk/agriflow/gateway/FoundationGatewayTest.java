package lk.agriflow.gateway;

import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class FoundationGatewayTest {
    static final AtomicInteger UPSTREAM_STATUS = new AtomicInteger(200);
    static final AtomicInteger UPSTREAM_REQUESTS = new AtomicInteger();
    static HttpServer upstream;

    @DynamicPropertySource
    static void upstream(DynamicPropertyRegistry properties) throws Exception {
        upstream = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        upstream.createContext("/", exchange -> {
            UPSTREAM_REQUESTS.incrementAndGet();
            var body = (exchange.getRequestURI().getPath().equals("/api/v1/system")
                ? "{\"stage\":\"foundation\"}" : "[{\"name\":\"Synthetic produce\",\"unit\":\"kg\"}]")
                .getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().add("Content-Type", "application/json");
            exchange.getResponseHeaders().add("Set-Cookie", "upstream-private=do-not-forward");
            exchange.getResponseHeaders().add("Location", "https://example.invalid/private");
            exchange.sendResponseHeaders(UPSTREAM_STATUS.get(), body.length);
            exchange.getResponseBody().write(body);
            exchange.close();
        });
        upstream.start();
        properties.add("MARKET_CORE_URL", () -> "http://127.0.0.1:" + upstream.getAddress().getPort());
    }

    @AfterAll static void stop() { if (upstream != null) upstream.stop(0); }
    @BeforeEach void reset() { UPSTREAM_STATUS.set(200); UPSTREAM_REQUESTS.set(0); }
    @Autowired MockMvc mvc;

    @Test void publicCatalogAndSystemReachMarketWithoutLeakingHeaders() throws Exception {
        mvc.perform(get("/api/v1/catalog/produce"))
            .andExpect(status().isOk()).andExpect(jsonPath("$[0].unit").value("kg"))
            .andExpect(header().doesNotExist("Set-Cookie"))
            .andExpect(header().doesNotExist("Location"));
        mvc.perform(get("/api/v1/system"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.stage").value("foundation"));
    }

    @Test void upstreamFailureReturnsUnavailableWithoutFabricatedCatalog() throws Exception {
        UPSTREAM_STATUS.set(500);
        mvc.perform(get("/api/v1/catalog/produce"))
            .andExpect(status().isServiceUnavailable())
            .andExpect(jsonPath("$.title").value("Market service unavailable"));
    }

    @Test void upstreamRedirectDoesNotEscapeTheGateway() throws Exception {
        UPSTREAM_STATUS.set(302);
        mvc.perform(get("/api/v1/catalog/produce"))
            .andExpect(status().isServiceUnavailable()).andExpect(header().doesNotExist("Location"));
    }

    @Test void protectedRequestsNeverReachTheUpstream() throws Exception {
        mvc.perform(get("/api/v1/private" )).andExpect(status().isUnauthorized());
        mvc.perform(post("/api/v1/catalog/produce")).andExpect(status().isForbidden());
        org.junit.jupiter.api.Assertions.assertEquals(0, UPSTREAM_REQUESTS.get());
    }
}
