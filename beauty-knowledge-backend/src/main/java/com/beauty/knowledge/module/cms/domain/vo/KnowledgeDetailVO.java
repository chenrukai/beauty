package com.beauty.knowledge.module.cms.domain.vo;

import com.beauty.knowledge.module.cms.domain.entity.KbFile;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class KnowledgeDetailVO {

    private KbKnowledge knowledge;
    private List<KbFile> files;
}
