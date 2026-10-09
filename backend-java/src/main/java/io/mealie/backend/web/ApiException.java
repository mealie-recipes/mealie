package io.mealie.backend.web;

import java.util.Map;
import org.springframework.http.HttpStatus;

/** The equivalent of FastAPI's HTTPException; rendered as {@code {"detail": ...}} by {@link ApiExceptionHandler}. */
public class ApiException extends RuntimeException {

    private final HttpStatus status;
    private final Map<String, String> headers;

    public ApiException(HttpStatus status, String detail, Map<String, String> headers) {
        super(detail);
        this.status = status;
        this.headers = Map.copyOf(headers);
    }

    /** FastAPI's default detail is the reason phrase, e.g. {@code HTTPException(401)} gives "Unauthorized". */
    public ApiException(HttpStatus status) {
        this(status, status.getReasonPhrase(), Map.of());
    }

    public HttpStatus status() {
        return status;
    }

    public String detail() {
        return getMessage();
    }

    public Map<String, String> headers() {
        return headers;
    }
}
