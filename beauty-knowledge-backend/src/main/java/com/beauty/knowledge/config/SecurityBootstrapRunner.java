package com.beauty.knowledge.config;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.module.auth.domain.entity.SysUser;
import com.beauty.knowledge.module.auth.mapper.SysUserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Slf4j
@Component
@RequiredArgsConstructor
public class SecurityBootstrapRunner implements CommandLineRunner {

    private static final String DEFAULT_ADMIN_HASH = "$2a$10$Xkzvqpccpw58aTSzFTliC./y3PIBlw31cd0EHgQl7lC4.g6A36cq2";

    private final SysUserMapper sysUserMapper;
    private final PasswordEncoder passwordEncoder;

    @Value("${beauty.security.disable-default-seed-users:true}")
    private boolean disableDefaultSeedUsers;

    @Value("${beauty.bootstrap.admin.enabled:false}")
    private boolean bootstrapAdminEnabled;

    @Value("${beauty.bootstrap.admin.username:}")
    private String bootstrapAdminUsername;

    @Value("${beauty.bootstrap.admin.password:}")
    private String bootstrapAdminPassword;

    @Override
    public void run(String... args) {
        log.info("Security bootstrap -> disableDefaultSeedUsers={}, bootstrapAdminEnabled={}",
                disableDefaultSeedUsers, bootstrapAdminEnabled);
        if (disableDefaultSeedUsers) {
            disableKnownSeedUsers();
            disableWeakDefaultAdmin();
        } else {
            log.warn("Security bootstrap -> default seed user auto-disable is OFF. Use only in trusted dev environments.");
        }
        if (bootstrapAdminEnabled) {
            bootstrapAdmin();
        } else {
            log.info("Security bootstrap -> bootstrap admin is disabled.");
        }
    }

    private void disableKnownSeedUsers() {
        updateUserStatus("trainer01", 0);
        updateUserStatus("staff01", 0);
        updateUserStatus("staff02", 0);
    }

    private void disableWeakDefaultAdmin() {
        SysUser admin = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getUsername, "admin")
                .last("limit 1"));
        if (admin == null) {
            return;
        }
        if (DEFAULT_ADMIN_HASH.equals(admin.getPassword()) && (admin.getStatus() == null || admin.getStatus() == 1)) {
            admin.setStatus(0);
            sysUserMapper.updateById(admin);
            log.warn("Security bootstrap -> default admin account was disabled (weak seeded password detected).");
            log.warn("Security bootstrap -> if needed, enable beauty.bootstrap.admin.enabled=true and set BEAUTY_BOOTSTRAP_ADMIN_USERNAME/PASSWORD.");
        }
    }

    private void bootstrapAdmin() {
        if (!StringUtils.hasText(bootstrapAdminUsername) || !StringUtils.hasText(bootstrapAdminPassword)) {
            log.warn("Security bootstrap -> admin bootstrap enabled but username/password is empty; skipping.");
            return;
        }
        SysUser existing = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getUsername, bootstrapAdminUsername)
                .last("limit 1"));
        if (existing == null) {
            SysUser user = new SysUser();
            user.setUsername(bootstrapAdminUsername);
            user.setPassword(passwordEncoder.encode(bootstrapAdminPassword));
            user.setNickname(bootstrapAdminUsername);
            user.setRole("admin");
            user.setStatus(1);
            sysUserMapper.insert(user);
            log.info("Security bootstrap -> admin account created: {}", bootstrapAdminUsername);
            return;
        }
        existing.setPassword(passwordEncoder.encode(bootstrapAdminPassword));
        existing.setRole("admin");
        existing.setStatus(1);
        sysUserMapper.updateById(existing);
        log.info("Security bootstrap -> admin account updated and enabled: {}", bootstrapAdminUsername);
    }

    private void updateUserStatus(String username, int status) {
        SysUser user = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getUsername, username)
                .last("limit 1"));
        if (user == null) {
            return;
        }
        if (user.getStatus() != null && user.getStatus() == status) {
            return;
        }
        user.setStatus(status);
        sysUserMapper.updateById(user);
        log.warn("Security bootstrap -> user {} was set to status {}", username, status);
    }
}
