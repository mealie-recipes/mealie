package io.mealie.backend.persistence.model;

import java.util.UUID;

/** Minimal public group projection required by the unauthenticated app-info endpoint. */
public record PublicGroupRow(UUID id, String slug) {
}
