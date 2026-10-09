package io.mealie.backend;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("io.mealie.backend.persistence.mapper")
public class MealieApplication {

    public static void main(String[] args) {
        SpringApplication.run(MealieApplication.class, args);
    }
}
