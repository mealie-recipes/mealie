package io.mealie.backend.health;

import io.mealie.backend.auth.AuthTokens;
import io.mealie.backend.health.HealthService.Health;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Java-only diagnostics. The path has no Python counterpart, and the gateway doesn't route it, so call it on :9100.
 * Answers 503 when the database can't be reached.
 */
@RestController
public class HealthController {

    private final HealthService healthService;

    public HealthController(HealthService healthService) {
        this.healthService = healthService;
    }

    @GetMapping("/api/java/health")
    ResponseEntity<Health> health(HttpServletRequest request) {
        Health health = healthService.check(AuthTokens.extract(request));
        HttpStatus status = health.database().connected() ? HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE;
        return ResponseEntity.status(status).body(health);
    }
}
