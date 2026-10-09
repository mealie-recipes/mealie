package io.mealie.backend.persistence.mapper;

import io.mealie.backend.persistence.model.PublicGroupRow;
import org.apache.ibatis.annotations.Param;

public interface AppInfoMapper {

    PublicGroupRow findPublicGroupByName(@Param("name") String name);

    String findPublicHouseholdSlug(@Param("groupId") Object groupId, @Param("name") String name);
}
