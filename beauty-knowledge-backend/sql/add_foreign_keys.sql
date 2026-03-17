-- Add relational constraints for data consistency.
-- Execute manually after confirming existing data quality:
-- USE beauty_knowledge; SOURCE add_foreign_keys.sql;

USE beauty_knowledge;

ALTER TABLE kb_knowledge
    ADD CONSTRAINT fk_kb_knowledge_category
        FOREIGN KEY (category_id) REFERENCES kb_category (id),
    ADD CONSTRAINT fk_kb_knowledge_author
        FOREIGN KEY (author_id) REFERENCES sys_user (id);

ALTER TABLE kb_file
    ADD CONSTRAINT fk_kb_file_knowledge
        FOREIGN KEY (knowledge_id) REFERENCES kb_knowledge (id) ON DELETE CASCADE;

ALTER TABLE kb_chunk
    ADD CONSTRAINT fk_kb_chunk_knowledge
        FOREIGN KEY (knowledge_id) REFERENCES kb_knowledge (id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_kb_chunk_file
        FOREIGN KEY (file_id) REFERENCES kb_file (id) ON DELETE CASCADE;

ALTER TABLE process_task
    ADD CONSTRAINT fk_process_task_file
        FOREIGN KEY (file_id) REFERENCES kb_file (id) ON DELETE CASCADE;

ALTER TABLE chat_session
    ADD CONSTRAINT fk_chat_session_user
        FOREIGN KEY (user_id) REFERENCES sys_user (id);

ALTER TABLE chat_message
    ADD CONSTRAINT fk_chat_message_session
        FOREIGN KEY (session_id) REFERENCES chat_session (id) ON DELETE CASCADE;

ALTER TABLE rel_ingredient_effect
    ADD CONSTRAINT fk_rel_ie_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES beauty_ingredient (id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_rel_ie_effect
        FOREIGN KEY (effect_id) REFERENCES beauty_effect (id) ON DELETE CASCADE;

ALTER TABLE rel_product_ingredient
    ADD CONSTRAINT fk_rel_pi_product
        FOREIGN KEY (product_id) REFERENCES beauty_product (id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_rel_pi_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES beauty_ingredient (id) ON DELETE CASCADE;

ALTER TABLE entity_extract_pending
    ADD CONSTRAINT fk_entity_pending_file
        FOREIGN KEY (file_id) REFERENCES kb_file (id) ON DELETE CASCADE;
