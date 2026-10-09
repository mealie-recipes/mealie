package io.mealie.backend.persistence.mapper;

import io.mealie.backend.persistence.model.UserAuthRow;
import org.apache.ibatis.annotations.Param;

public interface UserAuthMapper {

    UserAuthRow findById(@Param("id") Object id);

    UserAuthRow findByApiToken(@Param("token") String token, @Param("userId") Object userId);
}
