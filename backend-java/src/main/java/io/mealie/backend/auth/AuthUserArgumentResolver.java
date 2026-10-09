package io.mealie.backend.auth;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.core.MethodParameter;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.support.WebDataBinderFactory;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.method.support.ModelAndViewContainer;

/**
 * Lets a controller require auth by declaring an {@link AuthUser} parameter, the way Python routes declare
 * {@code Depends(get_current_user)}. A missing or invalid token produces the same 401 as Python.
 */
@Component
public class AuthUserArgumentResolver implements HandlerMethodArgumentResolver {

    private final AuthService authService;

    public AuthUserArgumentResolver(AuthService authService) {
        this.authService = authService;
    }

    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return parameter.getParameterType() == AuthUser.class;
    }

    @Override
    public AuthUser resolveArgument(MethodParameter parameter, ModelAndViewContainer mavContainer,
            NativeWebRequest webRequest, WebDataBinderFactory binderFactory) {
        HttpServletRequest request = webRequest.getNativeRequest(HttpServletRequest.class);
        return authService.authenticate(AuthTokens.extract(request).orElse(""));
    }
}
