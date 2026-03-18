package com.beauty.knowledge.module.cms.domain.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class FavoriteKnowledgeVO {

    private Long knowledgeId;
    private String title;
    private String summary;
    private String type;
    private String coverUrl;
    private Integer viewCount;
    private LocalDateTime favoriteAt;
}

