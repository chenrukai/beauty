package com.beauty.knowledge.module.system.service;

import com.beauty.knowledge.module.system.domain.dto.UserActionDTO;

public interface UserActionService {

    void record(UserActionDTO dto, String ip, String userAgent);
}

