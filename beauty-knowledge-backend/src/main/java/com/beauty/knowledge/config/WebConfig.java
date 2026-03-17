package com.beauty.knowledge.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.ArrayList;
import java.util.List;

@Configuration
@ConfigurationProperties(prefix = "beauty.cors")
@Data
public class WebConfig implements WebMvcConfigurer {

    private List<String> allowedOrigins = new ArrayList<>();

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        String[] origins = allowedOrigins == null ? new String[0] : allowedOrigins.toArray(new String[0]);
        registry.addMapping("/**")
                .allowedOriginPatterns(origins)
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
