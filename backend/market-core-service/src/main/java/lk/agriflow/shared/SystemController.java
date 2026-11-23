package lk.agriflow.shared;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class SystemController {
    @GetMapping("/api/v1/system")
    Map<String, String> system() {
        return Map.of("name", "Dambulla AgriFlow", "version", "0.1.0",
            "stage", "foundation", "timezone", "Asia/Colombo");
    }
}
