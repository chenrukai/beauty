package com.beauty.knowledge.module.system.service;

import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.module.system.domain.dto.NoticeSaveDTO;
import com.beauty.knowledge.module.system.domain.entity.SysNotice;

public interface NoticeService {

    PageResult<SysNotice> page(Long pageNum, Long pageSize, Integer status, String keyword);

    void save(NoticeSaveDTO dto);

    void update(Long id, NoticeSaveDTO dto);

    void setTop(Long id, Integer isTop);
}

