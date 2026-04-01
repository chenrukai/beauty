package com.beauty.knowledge.module.rag.service;

import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.infrastructure.ai.llm.LLMProvider;
import com.beauty.knowledge.infrastructure.ai.python.PythonAIClient;
import com.beauty.knowledge.infrastructure.storage.MinioStorageService;
import com.beauty.knowledge.module.entity.domain.entity.BeautyEffect;
import com.beauty.knowledge.module.entity.domain.entity.BeautyIngredient;
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.domain.entity.RelIngredientEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductIngredient;
import com.beauty.knowledge.module.entity.mapper.BeautyEffectMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyIngredientMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyProductMapper;
import com.beauty.knowledge.module.entity.mapper.RelIngredientEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductIngredientMapper;
import com.beauty.knowledge.module.kg.domain.entity.KgEvidence;
import com.beauty.knowledge.module.kg.mapper.KgEvidenceMapper;
import com.beauty.knowledge.module.rag.domain.dto.ChatMessage;
import com.beauty.knowledge.module.rag.domain.dto.ChatRequest;
import com.beauty.knowledge.module.rag.domain.dto.ChatStreamChunk;
import com.beauty.knowledge.module.rag.domain.dto.ChunkResult;
import com.beauty.knowledge.module.rag.domain.entity.ChatMessageEntity;
import com.beauty.knowledge.module.rag.domain.entity.ChatSession;
import com.beauty.knowledge.module.rag.domain.enums.IntentType;
import com.beauty.knowledge.module.rag.mapper.KbChunkSearchMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;

import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.Map;
import java.util.HashSet;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicReference;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.tika.Tika;

@Service
@RequiredArgsConstructor
public class ChatService {

    private final IntentService intentService;
    private final ContextService contextService;
    private final HybridSearchService hybridSearchService;
    private final PromptService promptService;
    private final ChatSessionService chatSessionService;
    private final ChatRecordService chatRecordService;
    private final KbChunkSearchMapper kbChunkSearchMapper;
    private final ObjectProvider<LLMProvider> llmProviderObjectProvider;
    private final PythonAIClient pythonAIClient;
    private final MinioStorageService minioStorageService;
    private final BeautyProductMapper beautyProductMapper;
    private final BeautyIngredientMapper beautyIngredientMapper;
    private final BeautyEffectMapper beautyEffectMapper;
    private final RelProductIngredientMapper relProductIngredientMapper;
    private final RelIngredientEffectMapper relIngredientEffectMapper;
    private final RelProductEffectMapper relProductEffectMapper;
    private final KgEvidenceMapper kgEvidenceMapper;
    private final Tika tika = new Tika();

    @Value("${beauty.rag.display-source-top:4}")
    private int displaySourceTop;
    @Value("${beauty.rag.display-source-context-radius:1}")
    private int displaySourceContextRadius;
    @Value("${beauty.rag.display-source-context-limit:3}")
    private int displaySourceContextLimit;
    @Value("${beauty.rag.upload-summary-max-chars:12000}")
    private int uploadSummaryMaxChars;
    @Value("${beauty.rag.upload-ask-max-chars:24000}")
    private int uploadAskMaxChars;

    private final Map<Long, UploadContext> uploadContextBySession = new ConcurrentHashMap<>();
    private static final Pattern MONEY_PATTERN = Pattern.compile("(?<!\\d)(\\d{3,6})(?:\\.\\d{1,2})?(?!\\d)");

    public Flux<ChatStreamChunk> streamChat(Long userId, ChatRequest request) {
        LLMProvider llmProvider = llmProviderObjectProvider.getIfAvailable();
        if (llmProvider == null) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "鏈壘鍒板彲鐢ㄧ殑LLMProvider");
        }

        Long sessionId = chatSessionService.getOrCreate(userId, request.getSessionId(), request.getQuestion());
        chatRecordService.saveUserQuestion(sessionId, request.getQuestion());

        IntentType intent = intentService.detect(request.getQuestion());
        List<ChunkResult> sources = hybridSearchService.search(request.getQuestion(), request.getCategoryId());
        List<ChunkResult> filteredSources = filterSourcesByQuestion(sources, request.getQuestion());
        String systemPrompt = promptService.buildSystemPrompt(intent, filteredSources);
        String kgInsightContext = buildKgInsightContext(request.getQuestion());
        String kgInsightSummary = buildKgInsightSummary(request.getQuestion());
        if (StringUtils.hasText(kgInsightContext)) {
            systemPrompt = systemPrompt + "\n\nKnowledge Graph Context (verified relations):\n"
                    + kgInsightContext
                    + "\nPlease prioritize this structured graph context together with cited KB chunks.";
        }
        final String finalSystemPrompt = systemPrompt;
        final String finalKgInsightSummary = kgInsightSummary;
        List<com.beauty.knowledge.infrastructure.ai.llm.dto.ChatMessage> history = contextService.getRecentHistory(userId).stream()
                .map(h -> com.beauty.knowledge.infrastructure.ai.llm.dto.ChatMessage.builder()
                        .role(h.getRole())
                        .content(h.getContent())
                        .build())
                .toList();

        AtomicReference<StringBuilder> answerRef = new AtomicReference<>(new StringBuilder());
        Flux<ChatStreamChunk> tokenFlux = llmProvider.streamChat(finalSystemPrompt, request.getQuestion(), history)
                .map(token -> {
                    answerRef.get().append(token);
                    return ChatStreamChunk.builder()
                            .type("token")
                            .content(token)
                            .sessionId(sessionId)
                            .build();
                });

        Flux<ChatStreamChunk> doneFlux = Mono.defer(() -> {
                    String current = answerRef.get().toString();
                    if (current != null && !current.isBlank()) {
                        return Mono.just(current);
                    }
                    // Stream may fail on some local models; fallback once to non-stream chat.
                    return llmProvider.chatAsync(finalSystemPrompt, request.getQuestion())
                            .defaultIfEmpty("");
                })
                .map(answer -> {
                    String finalAnswer = (answer == null || answer.isBlank())
                            ? "AI service is temporarily unavailable. Please check Ollama/model configuration and try again."
                            : answer;
                    if (StringUtils.hasText(finalKgInsightSummary) && !finalAnswer.contains("【图谱洞察摘要】")) {
                        finalAnswer = "【图谱洞察摘要】" + finalKgInsightSummary + "\n\n" + finalAnswer;
                    }
                    List<ChunkResult> displaySources = buildDisplaySources(filteredSources);
                    chatRecordService.saveAssistantAnswer(sessionId, finalAnswer, displaySources);
                    contextService.appendRound(userId, request.getQuestion(), finalAnswer);
                    return ChatStreamChunk.builder()
                            .type("done")
                            .content(finalAnswer)
                            .sessionId(sessionId)
                            .sources(displaySources)
                            .build();
                })
                .subscribeOn(Schedulers.boundedElastic())
                .flux();
        return tokenFlux.concatWith(doneFlux);
    }

    public List<ChatSession> listSessions(Long userId) {
        return chatSessionService.listByUser(userId);
    }

    public ChatSession createSession(Long userId) {
        return chatSessionService.createEmpty(userId);
    }

    public List<ChatMessageEntity> listMessages(Long userId, Long sessionId) {
        List<ChatSession> sessions = chatSessionService.listByUser(userId);
        boolean owned = sessions.stream().anyMatch(s -> s.getId().equals(sessionId));
        if (!owned) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "会话不存在");
        }
        return chatRecordService.listBySession(sessionId);
    }

    public void deleteSession(Long userId, Long sessionId) {
        chatSessionService.delete(userId, sessionId);
    }

    public UploadSummaryResult summarizeUpload(Long userId, MultipartFile file, String instruction, Long sessionId) {
        if (file == null || file.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "涓婁紶鏂囦欢涓嶈兘涓虹┖");
        }
        LLMProvider llmProvider = llmProviderObjectProvider.getIfAvailable();
        if (llmProvider == null) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "鏈壘鍒板彲鐢ㄧ殑LLMProvider");
        }

        String extractedText = extractUploadText(file);
        if (!StringUtils.hasText(extractedText)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "文件内容为空或无法解析");
        }
        String fileName = safeFileName(file.getOriginalFilename());
        String contentType = StringUtils.hasText(file.getContentType()) ? file.getContentType() : "application/octet-stream";
        String minioPath = minioStorageService.buildPath("chat-upload", fileName);
        try {
            minioStorageService.upload(file.getBytes(), minioPath, contentType);
        } catch (Exception ex) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "附件保存失败，请重试");
        }
        PriceFacts facts = extractPriceFacts(extractedText);
        String clipped = extractedText.length() > uploadSummaryMaxChars
                ? extractedText.substring(0, uploadSummaryMaxChars)
                : extractedText;

        String finalInstruction = StringUtils.hasText(instruction)
                ? instruction.trim()
                : "璇锋€荤粨杩欎釜鏂囦欢鍐呭";
        Long sid = chatSessionService.getOrCreate(userId, sessionId, finalInstruction);
        uploadContextBySession.put(sid, new UploadContext(
                fileName,
                extractedText,
                facts,
                minioPath,
                contentType
        ));
        String userQuestion = finalInstruction + "（附件：" + fileName + "）";
        chatRecordService.saveUserQuestion(sid, userQuestion);

        String systemPrompt = """
                浣犳槸鏂囨。鎬荤粨鍔╂墜銆傝涓ユ牸鍩轰簬鐢ㄦ埛涓婁紶鏂囦欢鍐呭鍥炵瓟銆?                杈撳嚭蹇呴』鏄函鏂囨湰锛屼笉瑕佷娇鐢?Markdown 绗﹀彿锛堝 #銆?銆?銆佹暟瀛楀垪琛ㄥ墠缂€锛夈€?                缁撴瀯瑕佹眰锛?                缁撹锛?                鍏抽敭瑕佺偣锛?                琛屽姩寤鸿锛?                鑻ユ枃浠朵俊鎭笉瓒筹紝鏄庣‘鎸囧嚭涓嶈冻锛屼笉瑕佺紪閫犮€?                """;
        String userPrompt = finalInstruction
                + "\n\n【结构化价格事实（优先使用）】\n"
                + renderPriceFactsForPrompt(facts)
                + "\n\n銆愭枃浠跺唴瀹广€慭n" + clipped;
        String answer = llmProvider.chatAsync(systemPrompt, userPrompt).block();
        String rawAnswer = StringUtils.hasText(answer)
                ? toPlainText(answer)
                : "AI service is temporarily unavailable. Please check Ollama/model configuration and try again.";
        String finalAnswer = enforcePriceFactConsistency(rawAnswer, facts);
        chatRecordService.saveAssistantAnswer(sid, finalAnswer, List.of());
        contextService.appendRound(userId, userQuestion, finalAnswer);
        return new UploadSummaryResult(sid, finalAnswer, fileName);
    }

    public UploadAskResult askByUploadedDocument(Long userId, Long sessionId, String question) {
        if (sessionId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "sessionId涓嶈兘涓虹┖");
        }
        if (!StringUtils.hasText(question)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "闂涓嶈兘涓虹┖");
        }
        ensureSessionOwned(userId, sessionId);
        UploadContext ctx = uploadContextBySession.get(sessionId);
        if (ctx == null || !StringUtils.hasText(ctx.content())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "褰撳墠浼氳瘽娌℃湁涓婁紶鏂囦欢涓婁笅鏂囷紝璇峰厛涓婁紶鏂囦欢");
        }

        LLMProvider llmProvider = llmProviderObjectProvider.getIfAvailable();
        if (llmProvider == null) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "鏈壘鍒板彲鐢ㄧ殑LLMProvider");
        }

        String clipped = ctx.content().length() > uploadAskMaxChars
                ? ctx.content().substring(0, uploadAskMaxChars)
                : ctx.content();
        PriceFacts facts = ctx.facts() == null ? extractPriceFacts(ctx.content()) : ctx.facts();
        String cleanQuestion = question.trim();
        String userQuestion = cleanQuestion + "（基于附件：" + ctx.fileName() + "）";
        chatRecordService.saveUserQuestion(sessionId, userQuestion);

        String systemPrompt = """
                浣犳槸鏂囨。闂瓟鍔╂墜銆傝浠呬緷鎹敤鎴蜂笂浼犵殑鏂囦欢鍐呭鍥炵瓟銆?                涓嶈缂栭€犳枃浠堕噷娌℃湁鐨勪俊鎭€?                杈撳嚭蹇呴』鏄函鏂囨湰锛屼笉瑕佷娇鐢?Markdown 绗﹀彿锛堝 #銆?銆?銆佹暟瀛楀垪琛ㄥ墠缂€锛夈€?                鑻ユ枃浠朵腑鎵句笉鍒扮瓟妗堬紝璇锋槑纭洖澶嶁€滄枃浠朵腑鏈壘鍒拌淇℃伅鈥濄€?                """;
        String userPrompt = "用户问题：" + cleanQuestion
                + "\n\n【结构化价格事实（优先使用）】\n"
                + renderPriceFactsForPrompt(facts)
                + "\n\n銆愭枃浠跺唴瀹广€慭n" + clipped;
        String answer = llmProvider.chatAsync(systemPrompt, userPrompt).block();
        String rawAnswer = StringUtils.hasText(answer)
                ? toPlainText(answer)
                : "AI service is temporarily unavailable. Please check Ollama/model configuration and try again.";
        String finalAnswer = enforcePriceFactConsistency(rawAnswer, facts);
        chatRecordService.saveAssistantAnswer(sessionId, finalAnswer, List.of());
        contextService.appendRound(userId, userQuestion, finalAnswer);
        return new UploadAskResult(sessionId, finalAnswer, ctx.fileName());
    }

    public UploadAttachment getSessionAttachment(Long userId, Long sessionId) {
        if (sessionId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "sessionId is required");
        }
        ensureSessionOwned(userId, sessionId);
        UploadContext ctx = uploadContextBySession.get(sessionId);
        if (ctx == null || !StringUtils.hasText(ctx.minioPath())) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "No upload attachment found for this session");
        }
        byte[] bytes = minioStorageService.download(ctx.minioPath());
        String contentType = StringUtils.hasText(ctx.contentType()) ? ctx.contentType() : "application/octet-stream";
        return new UploadAttachment(ctx.fileName(), contentType, bytes);
    }

    public Map<String, Object> productInsight(Long productId) {
        if (productId == null || productId <= 0) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "productId is required");
        }
        BeautyProduct product = beautyProductMapper.selectById(productId);
        if (product == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "product not found");
        }

        List<RelProductIngredient> productIngredients = relProductIngredientMapper.selectList(
                new LambdaQueryWrapper<RelProductIngredient>()
                        .eq(RelProductIngredient::getProductId, productId)
                        .eq(RelProductIngredient::getStatus, "ACTIVE")
                        .orderByDesc(RelProductIngredient::getConfidence)
                        .orderByDesc(RelProductIngredient::getId)
        );

        Set<Long> ingredientIdSet = new LinkedHashSet<>();
        for (RelProductIngredient rel : productIngredients) {
            if (rel != null && rel.getIngredientId() != null) {
                ingredientIdSet.add(rel.getIngredientId());
            }
        }
        List<Long> ingredientIds = new ArrayList<>(ingredientIdSet);
        Map<Long, String> ingredientNameById = new ConcurrentHashMap<>();
        if (!ingredientIds.isEmpty()) {
            List<BeautyIngredient> ingredientRows = beautyIngredientMapper.selectBatchIds(ingredientIds);
            if (ingredientRows != null) {
                for (BeautyIngredient row : ingredientRows) {
                    if (row != null && row.getId() != null) {
                        ingredientNameById.put(row.getId(), row.getName());
                    }
                }
            }
        }

        List<RelIngredientEffect> ingredientEffects = ingredientIds.isEmpty()
                ? List.of()
                : relIngredientEffectMapper.selectList(
                new LambdaQueryWrapper<RelIngredientEffect>()
                        .in(RelIngredientEffect::getIngredientId, ingredientIds)
                        .eq(RelIngredientEffect::getStatus, "ACTIVE")
                        .orderByDesc(RelIngredientEffect::getConfidence)
                        .orderByDesc(RelIngredientEffect::getId)
        );

        List<RelProductEffect> productEffects = relProductEffectMapper.selectList(
                new LambdaQueryWrapper<RelProductEffect>()
                        .eq(RelProductEffect::getProductId, productId)
                        .eq(RelProductEffect::getStatus, "ACTIVE")
                        .orderByDesc(RelProductEffect::getConfidence)
                        .orderByDesc(RelProductEffect::getId)
        );

        Set<Long> inferredEffectIds = new LinkedHashSet<>();
        for (RelIngredientEffect rel : ingredientEffects) {
            if (rel != null && rel.getEffectId() != null) {
                inferredEffectIds.add(rel.getEffectId());
            }
        }
        Set<Long> directEffectIds = new LinkedHashSet<>();
        for (RelProductEffect rel : productEffects) {
            if (rel != null && rel.getEffectId() != null) {
                directEffectIds.add(rel.getEffectId());
            }
        }

        Set<Long> allEffectIds = new LinkedHashSet<>(inferredEffectIds);
        allEffectIds.addAll(directEffectIds);
        Map<Long, String> effectNameById = new ConcurrentHashMap<>();
        if (!allEffectIds.isEmpty()) {
            List<BeautyEffect> effectRows = beautyEffectMapper.selectBatchIds(allEffectIds);
            if (effectRows != null) {
                for (BeautyEffect row : effectRows) {
                    if (row != null && row.getId() != null) {
                        effectNameById.put(row.getId(), row.getName());
                    }
                }
            }
        }

        List<String> ingredientNames = toNameList(ingredientIds, ingredientNameById, 8);
        List<String> directEffectNames = toNameList(new ArrayList<>(directEffectIds), effectNameById, 8);
        List<String> inferredEffectNames = toNameList(new ArrayList<>(inferredEffectIds), effectNameById, 10);

        List<String> chains = new ArrayList<>();
        for (RelIngredientEffect rel : ingredientEffects) {
            if (rel == null || rel.getIngredientId() == null || rel.getEffectId() == null) {
                continue;
            }
            String ingredientName = ingredientNameById.getOrDefault(rel.getIngredientId(), "INGREDIENT:" + rel.getIngredientId());
            String effectName = effectNameById.getOrDefault(rel.getEffectId(), "EFFECT:" + rel.getEffectId());
            chains.add(product.getName() + " -> " + ingredientName + " -> " + effectName);
            if (chains.size() >= 8) {
                break;
            }
        }

        int evidenceCount = 0;
        for (RelProductIngredient rel : productIngredients) {
            if (rel == null || rel.getIngredientId() == null) {
                continue;
            }
            evidenceCount += countEvidence("PRODUCT_CONTAINS_INGREDIENT", "PRODUCT", productId, "INGREDIENT", rel.getIngredientId());
        }
        for (RelIngredientEffect rel : ingredientEffects) {
            if (rel == null || rel.getIngredientId() == null || rel.getEffectId() == null) {
                continue;
            }
            evidenceCount += countEvidence("INGREDIENT_HAS_EFFECT", "INGREDIENT", rel.getIngredientId(), "EFFECT", rel.getEffectId());
        }
        for (RelProductEffect rel : productEffects) {
            if (rel == null || rel.getEffectId() == null) {
                continue;
            }
            evidenceCount += countEvidence("PRODUCT_TARGETS_EFFECT", "PRODUCT", productId, "EFFECT", rel.getEffectId());
        }

        String summary = "产品「" + product.getName() + "」已关联成分 " + ingredientIdSet.size()
                + " 个，功效 " + allEffectIds.size() + " 个（直连 " + directEffectIds.size() + "，推导 "
                + inferredEffectIds.size() + "），证据 " + evidenceCount + " 条。";

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("productId", product.getId());
        result.put("productName", product.getName());
        result.put("ingredientCount", ingredientIdSet.size());
        result.put("effectCount", allEffectIds.size());
        result.put("directEffectCount", directEffectIds.size());
        result.put("inferredEffectCount", inferredEffectIds.size());
        result.put("evidenceCount", evidenceCount);
        result.put("ingredients", ingredientNames);
        result.put("directEffects", directEffectNames);
        result.put("inferredEffects", inferredEffectNames);
        result.put("chains", chains);
        result.put("summary", summary);
        return result;
    }

    private String extractUploadText(MultipartFile file) {
        try {
            byte[] bytes = file.getBytes();
            boolean image = isImage(file);
            boolean video = isVideo(file);
            boolean audio = isAudio(file);
            if (audio) {
                throw new BusinessException(ErrorCode.BAD_REQUEST, "AUDIO_DISABLED: 当前项目不支持音频上传");
            }
            if (image) {
                try {
                    String ocr = pythonAIClient.ocr(bytes);
                    if (StringUtils.hasText(ocr)) {
                        return ocr.replace("\u0000", " ").trim();
                    }
                } catch (Exception ignore) {
                    // fallback to tika
                }
            }
            if (video) {
                try {
                    String text = pythonAIClient.transcribe(bytes, "video");
                    if (StringUtils.hasText(text)) {
                        return text.replace("\u0000", " ").trim();
                    }
                } catch (Exception ignore) {
                    // fallback to tika
                }
            }
            String parsed = tika.parseToString(new ByteArrayInputStream(bytes));
            String clean = parsed == null ? "" : parsed.replace("\u0000", " ").trim();
            if (image && !StringUtils.hasText(clean)) {
                throw new BusinessException(
                        ErrorCode.BAD_REQUEST,
                        "IMAGE_TEXT_EMPTY: 当前仅支持图片文字识别，未检测到可识别文字。请上传包含清晰文字的图片，或改用文档后再提问。"
                );
            }
            if (video && !StringUtils.hasText(clean)) {
                throw new BusinessException(
                        ErrorCode.BAD_REQUEST,
                        "TRANSCRIBE_UNAVAILABLE: 褰撳墠鐜鏈惎鐢ㄨ棰?闊抽杞啓鏈嶅姟锛岃妫€鏌?Python transcribe 鎺ュ彛涓?ffmpeg"
                );
            }
            return clean;
        } catch (Exception e) {
            if (e instanceof BusinessException be) {
                throw be;
            }
            throw new BusinessException(ErrorCode.BAD_REQUEST, "鏂囦欢瑙ｆ瀽澶辫触");
        }
    }

    private String buildKgInsightContext(String question) {
        if (!StringUtils.hasText(question)) {
            return "";
        }
        try {
            BeautyProduct product = matchProductFromQuestion(question);
            if (product == null || product.getId() == null) {
                return "";
            }
            Map<String, Object> insight = productInsight(product.getId());
            String summary = String.valueOf(insight.getOrDefault("summary", ""));
            String ingredients = joinList(insight.get("ingredients"), 6);
            String directEffects = joinList(insight.get("directEffects"), 6);
            String inferredEffects = joinList(insight.get("inferredEffects"), 8);
            String chains = joinList(insight.get("chains"), 6);
            return "Product: " + product.getName()
                    + "\nSummary: " + summary
                    + "\nCore ingredients: " + ingredients
                    + "\nDirect effects: " + directEffects
                    + "\nInferred effects: " + inferredEffects
                    + "\nKey paths: " + chains;
        } catch (Exception ignore) {
            return "";
        }
    }

    private String buildKgInsightSummary(String question) {
        if (!StringUtils.hasText(question)) {
            return "";
        }
        try {
            BeautyProduct product = matchProductFromQuestion(question);
            if (product == null || product.getId() == null) {
                return "";
            }
            Map<String, Object> insight = productInsight(product.getId());
            int ingredientCount = toInt(insight.get("ingredientCount"));
            int effectCount = toInt(insight.get("effectCount"));
            int evidenceCount = toInt(insight.get("evidenceCount"));
            return "产品「" + product.getName() + "」关联成分 " + ingredientCount
                    + " 个，功效 " + effectCount + " 个，证据 " + evidenceCount + " 条。";
        } catch (Exception ignore) {
            return "";
        }
    }

    private BeautyProduct matchProductFromQuestion(String question) {
        String q = question.toLowerCase();
        String normalizedQ = normalizeProductKey(q);
        List<BeautyProduct> products = beautyProductMapper.selectList(new LambdaQueryWrapper<BeautyProduct>()
                .eq(BeautyProduct::getStatus, 1)
                .select(BeautyProduct::getId, BeautyProduct::getName));
        BeautyProduct best = null;
        int bestLen = 0;
        for (BeautyProduct p : products) {
            if (p == null || !StringUtils.hasText(p.getName())) {
                continue;
            }
            String name = p.getName().toLowerCase();
            String normalizedName = normalizeProductKey(name);
            boolean hit = q.contains(name) || (!normalizedName.isBlank() && normalizedQ.contains(normalizedName));
            if (hit && normalizedName.length() > bestLen) {
                best = p;
                bestLen = normalizedName.length();
            }
        }
        return best;
    }

    private int countEvidence(String relationType, String subjectType, Long subjectId, String objectType, Long objectId) {
        if (subjectId == null || objectId == null) {
            return 0;
        }
        Long cnt = kgEvidenceMapper.selectCount(new LambdaQueryWrapper<KgEvidence>()
                .eq(KgEvidence::getRelationType, relationType)
                .eq(KgEvidence::getSubjectType, subjectType)
                .eq(KgEvidence::getSubjectId, subjectId)
                .eq(KgEvidence::getObjectType, objectType)
                .eq(KgEvidence::getObjectId, objectId));
        return cnt == null ? 0 : cnt.intValue();
    }

    private List<String> toNameList(List<Long> ids, Map<Long, String> nameById, int limit) {
        List<String> out = new ArrayList<>();
        if (ids == null || ids.isEmpty()) {
            return out;
        }
        int max = Math.max(1, limit);
        for (Long id : ids) {
            if (id == null) {
                continue;
            }
            String name = nameById.get(id);
            if (!StringUtils.hasText(name)) {
                continue;
            }
            out.add(name);
            if (out.size() >= max) {
                break;
            }
        }
        return out;
    }

    private String joinList(Object raw, int limit) {
        if (!(raw instanceof List<?> list) || list.isEmpty()) {
            return "N/A";
        }
        List<String> out = new ArrayList<>();
        int max = Math.max(1, limit);
        for (Object item : list) {
            if (item == null) {
                continue;
            }
            out.add(String.valueOf(item));
            if (out.size() >= max) {
                break;
            }
        }
        return out.isEmpty() ? "N/A" : String.join(" | ", out);
    }

    private int toInt(Object raw) {
        if (raw == null) {
            return 0;
        }
        if (raw instanceof Number n) {
            return n.intValue();
        }
        try {
            return Integer.parseInt(String.valueOf(raw));
        } catch (Exception ignore) {
            return 0;
        }
    }

    private String normalizeProductKey(String text) {
        if (!StringUtils.hasText(text)) {
            return "";
        }
        return text.toLowerCase()
                .replace("＋", "+")
                .replaceAll("[\\s\\-_/·•,，。！？!?:：;；()（）\\[\\]{}]+", "")
                .trim();
    }

    private boolean isImage(MultipartFile file) {
        String contentType = file.getContentType();
        if (contentType != null && contentType.toLowerCase().startsWith("image/")) {
            return true;
        }
        String name = safeFileName(file.getOriginalFilename()).toLowerCase();
        return name.endsWith(".png")
                || name.endsWith(".jpg")
                || name.endsWith(".jpeg")
                || name.endsWith(".webp")
                || name.endsWith(".bmp")
                || name.endsWith(".gif");
    }

    private boolean isVideo(MultipartFile file) {
        String contentType = file.getContentType();
        if (contentType != null && contentType.toLowerCase().startsWith("video/")) {
            return true;
        }
        String name = safeFileName(file.getOriginalFilename()).toLowerCase();
        return name.endsWith(".mp4")
                || name.endsWith(".mov")
                || name.endsWith(".avi")
                || name.endsWith(".mkv")
                || name.endsWith(".webm")
                || name.endsWith(".m4v");
    }

    private boolean isAudio(MultipartFile file) {
        String contentType = file.getContentType();
        if (contentType != null && contentType.toLowerCase().startsWith("audio/")) {
            return true;
        }
        String name = safeFileName(file.getOriginalFilename()).toLowerCase();
        return name.endsWith(".mp3")
                || name.endsWith(".wav")
                || name.endsWith(".m4a")
                || name.endsWith(".aac")
                || name.endsWith(".flac")
                || name.endsWith(".ogg");
    }

    private String safeFileName(String name) {
        return StringUtils.hasText(name) ? name.trim() : "未命名文件";
    }

    private void ensureSessionOwned(Long userId, Long sessionId) {
        List<ChatSession> sessions = chatSessionService.listByUser(userId);
        boolean owned = sessions.stream().anyMatch(s -> s.getId().equals(sessionId));
        if (!owned) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "会话不存在");
        }
    }

    private PriceFacts extractPriceFacts(String text) {
        if (!StringUtils.hasText(text)) {
            return new PriceFacts(List.of(), List.of(), Set.of());
        }
        List<String> promo = new ArrayList<>();
        List<String> original = new ArrayList<>();
        Set<String> all = new LinkedHashSet<>();
        String[] lines = text.split("\\r?\\n");
        for (String line : lines) {
            if (!StringUtils.hasText(line)) {
                continue;
            }
            String normalized = line.replaceAll("\\s+", "");
            List<String> amounts = extractMoneyNumbers(normalized);
            if (amounts.isEmpty()) {
                continue;
            }
            boolean hasPromo = containsAny(normalized, "秒杀价", "活动价", "折后价", "到手价", "团购价", "特价", "优惠价", "限时价");
            boolean hasOriginal = containsAny(normalized, "原价", "门市价", "吊牌价", "划线价");
            all.addAll(amounts);
            if (hasPromo) {
                promo.addAll(amounts);
            } else if (hasOriginal) {
                original.addAll(amounts);
            }
        }
        // Fallback: if labels are missing, infer by magnitude (smaller as promo, larger as original).
        if (promo.isEmpty() && original.isEmpty() && all.size() >= 2) {
            List<Integer> nums = all.stream().map(Integer::parseInt).sorted().toList();
            promo.add(String.valueOf(nums.get(0)));
            original.add(String.valueOf(nums.get(nums.size() - 1)));
        }
        return new PriceFacts(
                new ArrayList<>(new LinkedHashSet<>(promo)),
                new ArrayList<>(new LinkedHashSet<>(original)),
                new LinkedHashSet<>(all)
        );
    }

    private List<String> extractMoneyNumbers(String text) {
        List<String> out = new ArrayList<>();
        Matcher m = MONEY_PATTERN.matcher(text);
        while (m.find()) {
            out.add(m.group(1));
        }
        return out;
    }

    private boolean containsAny(String text, String... keywords) {
        for (String k : keywords) {
            if (text.contains(k)) {
                return true;
            }
        }
        return false;
    }

    private String renderPriceFactsForPrompt(PriceFacts facts) {
        if (facts == null || facts.allPrices().isEmpty()) {
            return "未提取到明确价格；若内容涉及价格，请明确说明不确定。";
        }
        String promo = facts.promoPrices().isEmpty() ? "未识别" : String.join("、", withYuan(facts.promoPrices()));
        String original = facts.originalPrices().isEmpty() ? "未识别" : String.join("、", withYuan(facts.originalPrices()));
        return "活动/秒杀价: " + promo + "\n原价: " + original + "\n可引用价格全集: " + String.join("、", withYuan(new ArrayList<>(facts.allPrices())));
    }

    private List<String> withYuan(List<String> prices) {
        List<String> out = new ArrayList<>();
        for (String p : prices) {
            out.add(p + "元");
        }
        return out;
    }

    private String enforcePriceFactConsistency(String answer, PriceFacts facts) {
        if (!StringUtils.hasText(answer) || facts == null || facts.allPrices().isEmpty()) {
            return answer;
        }
        Set<String> allowed = new HashSet<>(facts.allPrices());
        String[] sentences = answer.split("[。！？\\n]");
        for (String sentence : sentences) {
            if (!containsAny(sentence, "价", "元", "价格", "优惠", "折后", "秒杀")) {
                continue;
            }
            Matcher m = MONEY_PATTERN.matcher(sentence);
            while (m.find()) {
                String n = m.group(1);
                if (!allowed.contains(n)) {
                    return buildPriceSafeFallback(facts, answer);
                }
            }
        }
        return answer;
    }

    private String buildPriceSafeFallback(PriceFacts facts, String originalAnswer) {
        StringBuilder sb = new StringBuilder();
        sb.append("结论：图片中价格信息已按可识别事实校正。\n");
        if (!facts.promoPrices().isEmpty()) {
            sb.append("活动/秒杀价：").append(String.join("、", withYuan(facts.promoPrices()))).append("。\n");
        }
        if (!facts.originalPrices().isEmpty()) {
            sb.append("原价：").append(String.join("、", withYuan(facts.originalPrices()))).append("。\n");
        }
        sb.append("说明：其余描述以图片可识别文本为准；如需更高准确率，请上传更高清原图。");
        if (StringUtils.hasText(originalAnswer) && !facts.promoPrices().isEmpty()) {
            sb.append("\n\n补充：已自动忽略与上述价格事实不一致的数字描述。");
        }
        return sb.toString();
    }

    private String toPlainText(String raw) {
        if (!StringUtils.hasText(raw)) {
            return "";
        }
        return raw
                .replace("\r", "")
                .replaceAll("(?m)^#{1,6}\\s*", "")
                .replaceAll("\\*\\*(.*?)\\*\\*", "$1")
                .replaceAll("\\*(.*?)\\*", "$1")
                .replaceAll("(?m)^\\s*[-*+]\\s+", "")
                .replaceAll("(?m)^\\s*\\d+\\.\\s+", "")
                .replace("`", "")
                .replaceAll("\n{3,}", "\n\n")
                .trim();
    }

    public record UploadSummaryResult(Long sessionId, String summary, String fileName) {}
    private record UploadContext(String fileName, String content, PriceFacts facts, String minioPath, String contentType) {}
    private record PriceFacts(List<String> promoPrices, List<String> originalPrices, Set<String> allPrices) {}
    public record UploadAskResult(Long sessionId, String answer, String fileName) {}
    public record UploadAttachment(String fileName, String contentType, byte[] bytes) {}

    private List<ChunkResult> filterSourcesByQuestion(List<ChunkResult> sources, String question) {
        if (sources == null || sources.isEmpty() || !StringUtils.hasText(question)) {
            return sources == null ? List.of() : sources;
        }
        String q = normalizeForMatch(question);
        List<String> keywords = extractKeywords(q);
        if (keywords.isEmpty()) {
            return sources;
        }
        double topScore = sources.stream()
                .filter(Objects::nonNull)
                .mapToDouble(ChunkResult::getScore)
                .max()
                .orElse(0D);
        double minScore = topScore > 0D ? topScore * 0.5D : 0D;

        List<ChunkResult> out = new ArrayList<>();
        for (ChunkResult s : sources) {
            if (s == null) {
                continue;
            }
            double score = s.getScore();
            if (score < minScore) {
                continue;
            }
            String content = normalizeForMatch(s.getContent());
            if (!StringUtils.hasText(content)) {
                continue;
            }
            int hit = 0;
            for (String k : keywords) {
                if (content.contains(k)) {
                    hit++;
                }
            }
            if (hit == 0) {
                continue;
            }
            out.add(s);
        }
        return out.isEmpty() ? List.of() : out;
    }

    private String normalizeForMatch(String text) {
        if (!StringUtils.hasText(text)) {
            return "";
        }
        return text.replaceAll("\\s+", "").toLowerCase();
    }

    private List<String> extractKeywords(String text) {
        List<String> out = new ArrayList<>();
        if (!StringUtils.hasText(text)) {
            return out;
        }
        // Keep alnum words
        String[] parts = text.split("[^a-z0-9]+");
        for (String p : parts) {
            if (p.length() >= 2) {
                out.add(p);
            }
        }
        // Add CJK bi-grams to avoid single-character noise
        for (int i = 0; i < text.length() - 1; i++) {
            char c1 = text.charAt(i);
            char c2 = text.charAt(i + 1);
            if (isCjk(c1) && isCjk(c2)) {
                out.add("" + c1 + c2);
            }
        }
        // Deduplicate while preserving order
        return new ArrayList<>(new LinkedHashSet<>(out));
    }

    private boolean isCjk(char ch) {
        Character.UnicodeBlock block = Character.UnicodeBlock.of(ch);
        return block == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS
                || block == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS_EXTENSION_A
                || block == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS_EXTENSION_B
                || block == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS_EXTENSION_C
                || block == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS_EXTENSION_D
                || block == Character.UnicodeBlock.CJK_COMPATIBILITY_IDEOGRAPHS;
    }

    private List<ChunkResult> buildDisplaySources(List<ChunkResult> sources) {
        if (sources == null || sources.isEmpty()) {
            return List.of();
        }
        int top = Math.max(1, displaySourceTop);
        List<ChunkResult> sorted = new ArrayList<>(sources);
        sorted.sort(Comparator.comparingDouble(ChunkResult::getScore).reversed()
                .thenComparing(ChunkResult::getRank));

        Set<String> seen = new LinkedHashSet<>();
        List<ChunkResult> out = new ArrayList<>();
        for (ChunkResult s : sorted) {
            if (s == null) {
                continue;
            }
            String normalized = normalizeContent(s.getContent());
            String key = (s.getFileId() == null ? 0L : s.getFileId()) + "#"
                    + (s.getPageNo() == null ? 0 : s.getPageNo()) + "#"
                    + normalized;
            if (!seen.add(key)) {
                continue;
            }
            out.add(enrichSourceContentForDisplay(s));
            if (out.size() >= top) {
                break;
            }
        }
        return out;
    }

    private String normalizeContent(String content) {
        if (content == null) {
            return "";
        }
        String normalized = content.replaceAll("\\s+", "");
        int maxLen = 120;
        if (normalized.length() > maxLen) {
            return normalized.substring(0, maxLen);
        }
        return normalized;
    }

    private ChunkResult enrichSourceContentForDisplay(ChunkResult source) {
        if (source == null || source.getFileId() == null || source.getChunkIndex() == null) {
            return source;
        }
        try {
            int radius = Math.max(0, displaySourceContextRadius);
            int limit = Math.max(1, displaySourceContextLimit);
            int start = Math.max(0, source.getChunkIndex() - radius);
            int end = source.getChunkIndex() + radius;
            List<ChunkResult> context = kbChunkSearchMapper.selectContextByRange(source.getFileId(), start, end, limit);
            if (context == null || context.isEmpty()) {
                return source;
            }
            List<ChunkResult> samePage = context.stream()
                    .filter(c -> c != null && (source.getPageNo() == null || source.getPageNo().equals(c.getPageNo())))
                    .toList();
            List<ChunkResult> used = samePage.isEmpty() ? context : samePage;
            List<ChunkResult> ordered = used.stream()
                    .sorted(Comparator.comparing(c -> c.getChunkIndex() == null ? Integer.MAX_VALUE : c.getChunkIndex()))
                    .toList();

            List<String> uniqueParts = new ArrayList<>();
            List<String> seenNormalized = new ArrayList<>();
            for (ChunkResult c : ordered) {
                if (c == null || c.getContent() == null || c.getContent().isBlank()) {
                    continue;
                }
                String raw = c.getContent().trim();
                String normalized = normalizeContent(raw);
                if (normalized.isBlank()) {
                    continue;
                }
                boolean duplicated = false;
                for (String seen : seenNormalized) {
                    if (seen.equals(normalized) || seen.contains(normalized) || normalized.contains(seen)) {
                        duplicated = true;
                        break;
                    }
                }
                if (duplicated) {
                    continue;
                }
                seenNormalized.add(normalized);
                uniqueParts.add(raw);
            }

            String mergedContent = uniqueParts.isEmpty()
                    ? source.getContent()
                    : String.join("\n", uniqueParts);
            source.setContent(mergedContent);
            return source;
        } catch (Exception ex) {
            return source;
        }
    }
}
