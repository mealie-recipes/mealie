package io.mealie.backend.web;

import java.util.Map;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

/** Renders errors with the same body shape as the Python backend so the diff test can compare them. */
@RestControllerAdvice
public class ApiExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(ApiException.class)
    ResponseEntity<Object> handleApiException(ApiException e) {
        ResponseEntity.BodyBuilder response = ResponseEntity.status(e.status());
        e.headers().forEach(response::header);
        return response.body(Map.of("detail", e.detail()));
    }

    /** Spring MVC's own errors (unknown path, wrong method, ...); Starlette answers these with the reason phrase. */
    @Override
    protected ResponseEntity<Object> createResponseEntity(Object body, HttpHeaders headers, HttpStatusCode statusCode,
            WebRequest request) {
        HttpStatus status = HttpStatus.resolve(statusCode.value());
        String detail = status != null ? status.getReasonPhrase() : String.valueOf(statusCode.value());
        return new ResponseEntity<>(Map.of("detail", detail), headers, statusCode);
    }
}
