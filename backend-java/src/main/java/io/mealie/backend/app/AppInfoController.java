package io.mealie.backend.app;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AppInfoController {

    private final AppInfoService service;

    public AppInfoController(AppInfoService service) {
        this.service = service;
    }

    @GetMapping("/api/app/about")
    AppInfo getAppInfo() {
        return service.get();
    }
}
