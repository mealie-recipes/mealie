As Mealie has become more popular and widely used we've started to receive anonymous reports from white-hats about security issues in the application. These are reported only to the maintainer of the project and remain private until they are fixed. We will try to fix these issues as soon as possible. We will also document security fixes in the changelog and release notes as well as keep track of the security issues that have been resolved on this page.

## [v1.0.0beta-x] Recipe Assets: Remote Code Execution

!!! error CWE-1336: Improper Neutralization of Special Elements Used in a Template Engine
    As a low privileged user, Create a new recipe and click on the "+" to add a New Asset.
    Select a file, then proxy the request that will create the asset.

    Since mealie/routes/recipe/recipe_crud_routes.py:306 is calling slugify on the name POST parameter, we use $ which slugify() will remove completely.

    Since mealie/routes/recipe/recipe_crud_routes.py:306 is concatenating raw user input from the extension POST parameter into the variable file_name, which ultimately gets used when writing to disk, we can use a directory traversal attack in the extension (e.g. ./../../../tmp/pwn.txt) to write the file to arbitrary location on the server.

    As an attacker, now that we have a strong attack primitive, we can start getting creative to get RCE. Since the files were being created by root, we could add an entry to /etc/passwd, create a crontab, etc. but since there was templating functionality in the application that peaked my interest. The PoC in the HTTP request above creates a Jinja2 template at /app/data/template/pwn.html. Since Jinja2 templates execute Python code when rendered, all we have to do now to get code execution is render the malicious template. This was easy enough.

### Mitigation

We've added proper path sanitization to ensure that the user is not allowed to write to arbitrary locations on the server.

## [All Versions] Markdown Editor: Cross Site Scripting

!!! error CWE-79: Cross-site Scripting (XSS) - Stored
    A low privilege user can insert malicious JavaScript code into the Recipe Instructions which will execute in another person's browser that visits the recipe.

    <img src=x onerror=alert(document.domain)>

### Mitigation

This issues is present on all pages that allow markdown input. This error has been mitigated by wrapping the 3rd Party Markdown component and using the `domPurify` library to strip out the dangerous HTML.

## [v1.0.0beta-x] Image Scraper: Server-Side Request Forgery

!!! error CWE-918: Server-Side Request Forgery (SSRF)
    In the recipe edit page, is possible to upload an image directly or via an URL provided by the user. The function that handles the fetching and saving of the image via the URL doesn't have any URL verification, which allows to fetch internal services.

    Furthermore, after the resource is fetch, there is no MIME type validation, which would ensure that the resource is indeed an image. After this, because there is no extension in the provided URL, the application will fallback to jpg, and original for the image name.

    Then the result is saved to disk with the original.jpg name, that can be retrieved from the following URL: http://<domain>/api/media/recipes/<recipe-uid>/images/original.jpg. This file will contain the full response of the provided URL.

    **Impact**

    An attacker can get sensitive information of any internal-only services running. For example, if the application is hosted on Amazon Web Services (AWS) plataform, its possible to fetch the AWS API endpoint, https://169.254.169.254, which returns API keys and other sensitive metadata.

### Mitigation

Two actions were taken to reduce exposure to SSRF in this case.

1. The application will not prevent requests being made to local resources by checking for localhost or 127.0.0.1 domain names.
2. The mime-type of the response is now checked prior to writing to disk.

If either of the above actions prevent the user from uploading images, the application will alert the user of what error occurred.
