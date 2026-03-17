package com.beauty.knowledge.infrastructure.dictionary;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CopyOnWriteArrayList;

@Slf4j
@Component
public class BeautyDictionary {

    private static final String DICT_PATH = "dictionary/beauty_terms.txt";
    private final List<String> terms = new CopyOnWriteArrayList<>();

    @PostConstruct
    public void init() {
        reload();
    }

    public List<String> match(String text) {
        if (text == null || text.isBlank()) {
            return List.of();
        }
        List<String> hits = new ArrayList<>();
        for (String term : terms) {
            if (text.contains(term)) {
                hits.add(term);
            }
        }
        hits.sort(Comparator.comparingInt(String::length).reversed());
        Set<String> unique = new LinkedHashSet<>(hits);
        return new ArrayList<>(unique);
    }

    public synchronized void reload() {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(
                new ClassPathResource(DICT_PATH).getInputStream(), StandardCharsets.UTF_8))) {
            List<String> loaded = reader.lines()
                    .map(String::trim)
                    .filter(s -> !s.isEmpty())
                    .filter(s -> !s.startsWith("#"))
                    .distinct()
                    .toList();
            terms.clear();
            terms.addAll(loaded);
            log.info("BeautyDictionary loaded {} terms", terms.size());
        } catch (Exception ex) {
            log.warn("BeautyDictionary reload failed: {}", ex.getMessage());
        }
    }
}
