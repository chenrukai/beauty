package com.beauty.knowledge.module.kg.domain.vo;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class KgBackfillResultVO {
    private Integer scannedProductIngredient;
    private Integer scannedIngredientEffect;
    private Integer scannedProductEffect;
    private Integer insertedEvidence;
    private Integer insertedProductEffect;
    private Integer updatedRelations;
}
