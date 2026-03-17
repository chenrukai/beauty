package com.beauty.knowledge.infrastructure.storage;

import io.minio.BucketExistsArgs;
import io.minio.GetObjectArgs;
import io.minio.MakeBucketArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.RemoveObjectArgs;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.time.LocalDate;
import java.util.Objects;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class MinioStorageService {

    private final MinioClient minioClient;

    @Value("${beauty.minio.bucket:beauty-knowledge}")
    private String bucket;

    @Value("${beauty.minio.endpoint:http://localhost:9000}")
    private String endpoint;

    public String buildPath(String fileType, String originalName) {
        String ext = "bin";
        if (originalName != null && originalName.contains(".")) {
            ext = originalName.substring(originalName.lastIndexOf('.') + 1).toLowerCase();
        }
        LocalDate now = LocalDate.now();
        return String.format("%s/%d/%02d/%02d/%s.%s",
                fileType,
                now.getYear(),
                now.getMonthValue(),
                now.getDayOfMonth(),
                UUID.randomUUID(),
                ext);
    }

    public String upload(byte[] bytes, String objectPath, String contentType) {
        try {
            ensureBucket();
            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectPath)
                            .stream(new ByteArrayInputStream(bytes), bytes.length, -1)
                            .contentType(contentType == null ? "application/octet-stream" : contentType)
                            .build()
            );
            return objectPath;
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO上传失败", ex);
        }
    }

    public byte[] download(String objectPath) {
        try (InputStream in = minioClient.getObject(GetObjectArgs.builder().bucket(bucket).object(objectPath).build())) {
            return in.readAllBytes();
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO下载失败", ex);
        }
    }

    public void delete(String objectPath) {
        try {
            minioClient.removeObject(RemoveObjectArgs.builder().bucket(bucket).object(objectPath).build());
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO删除失败", ex);
        }
    }

    public void remove(String objectPath) {
        delete(objectPath);
    }

    public String getAccessUrl(String objectPath) {
        String base = Objects.toString(endpoint, "").replaceAll("/+$", "");
        return base + "/" + bucket + "/" + objectPath;
    }

    private void ensureBucket() throws Exception {
        boolean exists = minioClient.bucketExists(BucketExistsArgs.builder().bucket(bucket).build());
        if (!exists) {
            minioClient.makeBucket(MakeBucketArgs.builder().bucket(bucket).build());
        }
    }
}
