package com.beauty.knowledge.module.entity.service;

import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.entity.domain.dto.EntityConfirmItemDTO;
import com.beauty.knowledge.module.entity.domain.entity.BeautyEffect;
import com.beauty.knowledge.module.entity.domain.entity.BeautyIngredient;
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class EntityConfirmService {

    private final EntityExtractPendingMapper pendingMapper;
    private final IngredientService ingredientService;
    private final EffectService effectService;
    private final ProductService productService;

    @Transactional(rollbackFor = Exception.class)
    public void confirmBatch(List<EntityConfirmItemDTO> items) {
        for (EntityConfirmItemDTO item : items) {
            EntityExtractPending pending = pendingMapper.selectById(item.getPendingId());
            if (pending == null || !"PENDING".equalsIgnoreCase(pending.getStatus())) {
                continue;
            }
            if (Boolean.TRUE.equals(item.getAccept())) {
                saveEntity(pending);
                pending.setStatus("CONFIRMED");
            } else {
                pending.setStatus("REJECTED");
            }
            pendingMapper.updateById(pending);
        }
    }

    private void saveEntity(EntityExtractPending pending) {
        switch (pending.getEntityType()) {
            case "ingredient" -> {
                BeautyIngredient i = new BeautyIngredient();
                i.setName(pending.getEntityName());
                i.setStatus(1);
                ingredientService.save(i);
            }
            case "effect" -> {
                BeautyEffect e = new BeautyEffect();
                e.setName(pending.getEntityName());
                e.setStatus(1);
                effectService.save(e);
            }
            case "product" -> {
                BeautyProduct p = new BeautyProduct();
                p.setName(pending.getEntityName());
                p.setBrand("待补充");
                p.setStatus(1);
                productService.save(p);
            }
            default -> throw new BusinessException(ErrorCode.BAD_REQUEST, "未知实体类型");
        }
    }
}
