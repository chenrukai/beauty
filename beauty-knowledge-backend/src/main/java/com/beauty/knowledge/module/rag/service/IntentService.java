package com.beauty.knowledge.module.rag.service;

import com.beauty.knowledge.module.rag.domain.enums.IntentType;
import org.springframework.stereotype.Service;

@Service
public class IntentService {

    public IntentType detect(String question) {
        String q = question == null ? "" : question.toLowerCase();
        if (q.contains("成分") || q.contains("烟酰胺") || q.contains("水杨酸")) {
            return IntentType.INGREDIENT;
        }
        if (q.contains("功效") || q.contains("修护") || q.contains("美白") || q.contains("补水")) {
            return IntentType.EFFECT;
        }
        if (q.contains("产品") || q.contains("推荐") || q.contains("用什么")) {
            return IntentType.PRODUCT;
        }
        return IntentType.GENERAL;
    }
}
