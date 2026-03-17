package com.beauty.knowledge.module.entity.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.mapper.BeautyProductMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final BeautyProductMapper productMapper;

    public List<BeautyProduct> list(String keyword) {
        return productMapper.selectList(new LambdaQueryWrapper<BeautyProduct>()
                .like(StringUtils.hasText(keyword), BeautyProduct::getName, keyword)
                .orderByDesc(BeautyProduct::getId));
    }

    @Transactional(rollbackFor = Exception.class)
    public void save(BeautyProduct entity) {
        checkNameUnique(entity.getName(), entity.getBrand(), null);
        if (entity.getStatus() == null) {
            entity.setStatus(1);
        }
        productMapper.insert(entity);
    }

    @Transactional(rollbackFor = Exception.class)
    public void update(Long id, BeautyProduct entity) {
        BeautyProduct db = productMapper.selectById(id);
        if (db == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "产品不存在");
        }
        checkNameUnique(entity.getName(), entity.getBrand(), id);
        db.setName(entity.getName());
        db.setBrand(entity.getBrand());
        db.setProductType(entity.getProductType());
        db.setSkinType(entity.getSkinType());
        db.setIntro(entity.getIntro());
        db.setStatus(entity.getStatus() == null ? 1 : entity.getStatus());
        productMapper.updateById(db);
    }

    @Transactional(rollbackFor = Exception.class)
    public void delete(Long id) {
        productMapper.deleteById(id);
    }

    public BeautyProduct getById(Long id) {
        return productMapper.selectById(id);
    }

    private void checkNameUnique(String name, String brand, Long excludeId) {
        BeautyProduct exist = productMapper.selectOne(new LambdaQueryWrapper<BeautyProduct>()
                .eq(BeautyProduct::getName, name)
                .eq(BeautyProduct::getBrand, brand)
                .ne(excludeId != null, BeautyProduct::getId, excludeId)
                .last("limit 1"));
        if (exist != null) {
            throw new BusinessException(ErrorCode.ENTITY_NAME_EXISTS);
        }
    }
}
