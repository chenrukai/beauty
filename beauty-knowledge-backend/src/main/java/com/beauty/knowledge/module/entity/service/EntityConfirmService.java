package com.beauty.knowledge.module.entity.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.entity.domain.dto.EntityConfirmBatchResultDTO;
import com.beauty.knowledge.module.entity.domain.dto.EntityConfirmItemDTO;
import com.beauty.knowledge.module.entity.domain.dto.EntityConfirmItemResultDTO;
import com.beauty.knowledge.module.entity.domain.entity.BeautyEffect;
import com.beauty.knowledge.module.entity.domain.entity.BeautyIngredient;
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.mapper.BeautyEffectMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyIngredientMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyProductMapper;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionDefinition;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class EntityConfirmService {

    private final EntityExtractPendingMapper pendingMapper;
    private final BeautyIngredientMapper ingredientMapper;
    private final BeautyEffectMapper effectMapper;
    private final BeautyProductMapper productMapper;
    private final PlatformTransactionManager transactionManager;

    public EntityConfirmBatchResultDTO confirmBatch(List<EntityConfirmItemDTO> items) {
        List<EntityConfirmItemResultDTO> results = new ArrayList<>();
        TransactionTemplate txTemplate = new TransactionTemplate(transactionManager);
        txTemplate.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRES_NEW);

        for (EntityConfirmItemDTO item : items) {
            try {
                EntityConfirmItemResultDTO one = txTemplate.execute(status -> processOne(item));
                if (one != null) {
                    results.add(one);
                }
            } catch (Exception ex) {
                results.add(EntityConfirmItemResultDTO.builder()
                        .pendingId(item == null ? null : item.getPendingId())
                        .accept(item == null ? null : item.getAccept())
                        .status("FAILED")
                        .message(ex.getMessage() == null ? "confirm failed" : ex.getMessage())
                        .build());
            }
        }

        int successCount = (int) results.stream().filter(r -> "SUCCESS".equalsIgnoreCase(r.getStatus())).count();
        int failedCount = results.size() - successCount;
        return EntityConfirmBatchResultDTO.builder()
                .total(items == null ? 0 : items.size())
                .successCount(successCount)
                .failedCount(failedCount)
                .itemResults(results)
                .build();
    }

    private EntityConfirmItemResultDTO processOne(EntityConfirmItemDTO item) {
        if (item == null || item.getPendingId() == null || item.getAccept() == null) {
            return EntityConfirmItemResultDTO.builder()
                    .pendingId(item == null ? null : item.getPendingId())
                    .accept(item == null ? null : item.getAccept())
                    .status("FAILED")
                    .message("invalid confirm item")
                    .build();
        }

        EntityExtractPending pending = pendingMapper.selectById(item.getPendingId());
        if (pending == null) {
            return EntityConfirmItemResultDTO.builder()
                    .pendingId(item.getPendingId())
                    .accept(item.getAccept())
                    .status("SKIPPED")
                    .message("pending record not found")
                    .build();
        }
        if (!"PENDING".equalsIgnoreCase(pending.getStatus())) {
            return EntityConfirmItemResultDTO.builder()
                    .pendingId(item.getPendingId())
                    .accept(item.getAccept())
                    .status("SKIPPED")
                    .message("pending record already processed")
                    .entityType(pending.getEntityType())
                    .entityName(pending.getEntityName())
                    .build();
        }

        if (Boolean.TRUE.equals(item.getAccept())) {
            saveEntityIfAbsent(pending);
            pending.setStatus("CONFIRMED");
        } else {
            pending.setStatus("REJECTED");
        }
        pendingMapper.updateById(pending);

        return EntityConfirmItemResultDTO.builder()
                .pendingId(item.getPendingId())
                .accept(item.getAccept())
                .status("SUCCESS")
                .message("ok")
                .entityType(pending.getEntityType())
                .entityName(pending.getEntityName())
                .build();
    }

    private void saveEntityIfAbsent(EntityExtractPending pending) {
        switch (pending.getEntityType()) {
            case "ingredient" -> saveIngredientIfAbsent(pending.getEntityName());
            case "effect" -> saveEffectIfAbsent(pending.getEntityName());
            case "product" -> saveProductIfAbsent(pending.getEntityName(), "pending");
            default -> throw new BusinessException(ErrorCode.BAD_REQUEST, "unknown entity type");
        }
    }

    private void saveIngredientIfAbsent(String name) {
        BeautyIngredient exists = ingredientMapper.selectOne(new LambdaQueryWrapper<BeautyIngredient>()
                .eq(BeautyIngredient::getName, name)
                .last("limit 1"));
        if (exists != null) {
            return;
        }
        BeautyIngredient i = new BeautyIngredient();
        i.setName(name);
        i.setStatus(1);
        ingredientMapper.insert(i);
    }

    private void saveEffectIfAbsent(String name) {
        BeautyEffect exists = effectMapper.selectOne(new LambdaQueryWrapper<BeautyEffect>()
                .eq(BeautyEffect::getName, name)
                .last("limit 1"));
        if (exists != null) {
            return;
        }
        BeautyEffect e = new BeautyEffect();
        e.setName(name);
        e.setStatus(1);
        effectMapper.insert(e);
    }

    private void saveProductIfAbsent(String name, String brand) {
        BeautyProduct exists = productMapper.selectOne(new LambdaQueryWrapper<BeautyProduct>()
                .eq(BeautyProduct::getName, name)
                .eq(BeautyProduct::getBrand, brand)
                .last("limit 1"));
        if (exists != null) {
            return;
        }
        BeautyProduct p = new BeautyProduct();
        p.setName(name);
        p.setBrand(brand);
        p.setStatus(1);
        productMapper.insert(p);
    }
}
