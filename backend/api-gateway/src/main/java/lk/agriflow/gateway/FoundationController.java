package lk.agriflow.gateway;

import java.net.http.HttpClient;
import java.time.Duration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

/** Narrow foundation routes; authenticated routing is implemented in Stage 03. */
@RestController
public class FoundationController {
    private final RestClient market;

    public FoundationController(@Value("${MARKET_CORE_URL:http://localhost:8082}") String baseUrl) {
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2))
            .followRedirects(HttpClient.Redirect.NEVER).build();
        var factory = new JdkClientHttpRequestFactory(client);
        factory.setReadTimeout(Duration.ofSeconds(4));
        market = RestClient.builder().baseUrl(baseUrl).requestFactory(factory).build();
    }

    @GetMapping("/api/v1/system")
    ResponseEntity<String> system() { return read("/api/v1/system"); }

    @GetMapping("/api/v1/catalog/produce")
    ResponseEntity<String> catalog() { return read("/api/v1/catalog/produce"); }

    private ResponseEntity<String> read(String path) {
        try {
            var response = market.get().uri(path).retrieve().toEntity(String.class);
            if (!response.getStatusCode().is2xxSuccessful()) {
                return unavailable();
            }
            return ResponseEntity.status(response.getStatusCode())
                .header("Content-Type", "application/json")
                .body(response.getBody());
        } catch (RestClientException unavailable) {
            return unavailable();
        }
    }

    private ResponseEntity<String> unavailable() {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
            .header("Content-Type", "application/problem+json")
            .body("{\"title\":\"Market service unavailable\",\"status\":503}");
    }
}
