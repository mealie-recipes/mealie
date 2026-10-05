<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

final class ImportService
{
    public function __construct(
        private readonly RecipeService $recipes,
        private readonly AiService $ai,
    ) {}

    /**
     * @return array<string, mixed>
     */
    public function fromUrl(object $user, string $url): array
    {
        $response = Http::timeout(20)->withHeaders(['User-Agent' => 'Mealie PHP'])->get($url);
        if (! $response->successful()) {
            throw new \RuntimeException('Could not fetch the page');
        }

        $recipe = $this->recipeFromHtml($response->body());
        if ($recipe === null) {
            throw new \RuntimeException('No recipe was found on that page');
        }

        $created = $this->recipes->create($user, ['name' => $recipe['name']]);
        $slug = (string) ($created['slug'] ?? '');

        return $this->recipes->update($user, $slug, $recipe) ?? $created;
    }

    /**
     * @return array<string, mixed>
     */
    public function fromDocument(object $user, string $body): array
    {
        $decoded = json_decode($body, true);
        $node = $this->findRecipe(is_array($decoded) ? $decoded : null);
        $recipe = $node !== null ? $this->mapRecipe($node) : $this->recipeFromHtml($body);
        if ($recipe === null) {
            throw new \RuntimeException('No recipe was found in that document');
        }
        $created = $this->recipes->create($user, ['name' => $recipe['name']]);

        return $this->recipes->update($user, (string) ($created['slug'] ?? ''), $recipe) ?? $created;
    }

    public function errorStream(string $message): string
    {
        return $this->event('error', ['message' => $message]);
    }

    public function streamAi(object $user, string $prompt): string
    {
        try {
            $recipe = $this->fromAi($user, $prompt);
        } catch (\Throwable $e) {
            return $this->event('error', ['message' => $e->getMessage()]);
        }

        return $this->event('progress', ['message' => 'Recipe created'])
            .$this->event('done', ['slug' => $recipe['slug'] ?? '']);
    }

    /**
     * @return array<string, mixed>
     */
    public function fromAi(object $user, string $prompt): array
    {
        $provider = $this->ai->defaultProvider($user);
        if ($provider === null) {
            throw new \RuntimeException('No AI provider is configured for recipe creation');
        }
        if (trim($prompt) === '') {
            throw new \RuntimeException('No recipe source was provided');
        }
        $base = rtrim((string) ($provider->base_url ?: 'https://api.openai.com/v1'), '/');
        $response = Http::timeout(max(10, (int) $provider->timeout))
            ->withToken((string) $provider->api_key)
            ->acceptJson()
            ->post($base.'/chat/completions', [
                'model' => $provider->model,
                'response_format' => ['type' => 'json_object'],
                'messages' => [
                    [
                        'role' => 'system',
                        'content' => 'Extract a cooking recipe. Reply with JSON only: name, description, recipeIngredient (array of strings), recipeInstructions (array of objects with text).',
                    ],
                    ['role' => 'user', 'content' => $prompt],
                ],
            ]);
        if (! $response->successful()) {
            throw new \RuntimeException('The AI provider rejected the request');
        }
        $content = (string) $response->json('choices.0.message.content');
        $content = trim(preg_replace('/^```(?:json)?|```$/m', '', $content) ?? $content);
        $decoded = json_decode($content, true);
        $node = $this->findRecipe(is_array($decoded) ? $decoded : null) ?? (is_array($decoded) ? $decoded : null);
        if (! is_array($node) || ! isset($node['name'])) {
            throw new \RuntimeException('The AI provider did not return a recipe');
        }
        $recipe = $this->mapRecipe($node);
        $created = $this->recipes->create($user, ['name' => $recipe['name']]);

        return $this->recipes->update($user, (string) ($created['slug'] ?? ''), $recipe) ?? $created;
    }

    public function stream(object $user, string $url): string
    {
        try {
            $recipe = $this->fromUrl($user, $url);
        } catch (\Throwable $e) {
            return $this->event('error', ['message' => $e->getMessage()]);
        }

        return $this->event('progress', ['message' => 'Recipe imported'])
            .$this->event('done', ['slug' => $recipe['slug'] ?? '']);
    }

    /**
     * @return array<string, mixed>|null
     */
    private function recipeFromHtml(string $html): ?array
    {
        if (preg_match_all('/<script[^>]*type=["\']application\/ld\+json["\'][^>]*>(.*?)<\/script>/si', $html, $matches)) {
            foreach ($matches[1] as $json) {
                $decoded = json_decode(html_entity_decode(trim($json)), true);
                $node = $this->findRecipe(is_array($decoded) ? $decoded : null);
                if ($node !== null) {
                    return $this->mapRecipe($node);
                }
            }
        }

        return $this->recipeFromMicrodata($html);
    }

    /**
     * @return array<string, mixed>|null
     */
    private function recipeFromMicrodata(string $html): ?array
    {
        if (! str_contains($html, 'schema.org/Recipe')) {
            return null;
        }
        $dom = new \DOMDocument;
        $previous = libxml_use_internal_errors(true);
        $loaded = $dom->loadHTML($html);
        libxml_clear_errors();
        libxml_use_internal_errors($previous);
        if (! $loaded) {
            return null;
        }
        $xpath = new \DOMXPath($dom);
        $nodes = $xpath->query('//*[@itemtype]');
        if ($nodes === false) {
            return null;
        }
        foreach ($nodes as $node) {
            if (! $node instanceof \DOMElement || ! preg_match('#schema\.org/Recipe\b#', $node->getAttribute('itemtype'))) {
                continue;
            }
            $name = $this->itemProp($xpath, $node, 'name');
            if ($name === '') {
                continue;
            }
            $ingredients = [];
            foreach ($this->itemProps($xpath, $node, 'recipeIngredient') as $line) {
                $ingredients[] = ['note' => $line, 'originalText' => $line, 'quantity' => 0];
            }
            $steps = [];
            foreach ($this->itemProps($xpath, $node, 'recipeInstructions') as $line) {
                $steps[] = ['text' => $line, 'title' => '', 'summary' => ''];
            }

            return [
                'name' => $name,
                'description' => $this->itemProp($xpath, $node, 'description'),
                'orgURL' => $this->itemProp($xpath, $node, 'url') ?: null,
                'recipeIngredient' => $ingredients,
                'recipeInstructions' => $steps,
            ];
        }

        return null;
    }

    private function itemProp(\DOMXPath $xpath, \DOMElement $context, string $name): string
    {
        $found = $this->itemProps($xpath, $context, $name);

        return $found[0] ?? '';
    }

    /**
     * @return list<string>
     */
    private function itemProps(\DOMXPath $xpath, \DOMElement $context, string $name): array
    {
        $nodes = $xpath->query('.//*[@itemprop="'.$name.'"]', $context);
        if ($nodes === false) {
            return [];
        }
        $values = [];
        foreach ($nodes as $node) {
            if (! $node instanceof \DOMElement) {
                continue;
            }
            $text = trim($node->getAttribute('content') ?: $node->textContent);
            if ($text !== '') {
                $values[] = $text;
            }
        }

        return $values;
    }

    /**
     * @return array<string, mixed>|null
     */
    private function findRecipe(mixed $node): ?array
    {
        if (! is_array($node)) {
            return null;
        }
        $type = $node['@type'] ?? null;
        $types = is_array($type) ? $type : [$type];
        if (in_array('Recipe', $types, true) && isset($node['name'])) {
            return $node;
        }
        foreach ($node['@graph'] ?? $node as $child) {
            if (! is_array($child)) {
                continue;
            }
            $found = $this->findRecipe($child);
            if ($found !== null) {
                return $found;
            }
        }

        return null;
    }

    /**
     * @param  array<string, mixed>  $node
     * @return array<string, mixed>
     */
    private function mapRecipe(array $node): array
    {
        $ingredients = [];
        foreach ($node['recipeIngredient'] ?? [] as $line) {
            if (is_string($line) && trim($line) !== '') {
                $ingredients[] = ['note' => trim($line), 'originalText' => trim($line), 'quantity' => 0];
            }
        }
        $steps = [];
        foreach ($node['recipeInstructions'] ?? [] as $step) {
            $text = is_string($step) ? $step : (is_array($step) ? ($step['text'] ?? '') : '');
            if (is_string($text) && trim($text) !== '') {
                $steps[] = ['text' => trim($text), 'title' => '', 'summary' => ''];
            }
        }

        return [
            'name' => is_string($node['name']) ? $node['name'] : 'Imported recipe',
            'description' => is_string($node['description'] ?? null) ? $node['description'] : '',
            'orgURL' => is_string($node['url'] ?? null) ? $node['url'] : null,
            'prepTime' => is_string($node['prepTime'] ?? null) ? $node['prepTime'] : null,
            'cookTime' => is_string($node['cookTime'] ?? null) ? $node['cookTime'] : null,
            'totalTime' => is_string($node['totalTime'] ?? null) ? $node['totalTime'] : null,
            'recipeYield' => is_string($node['recipeYield'] ?? null) ? $node['recipeYield'] : (isset($node['recipeYield']) ? (string) $node['recipeYield'] : null),
            'recipeIngredient' => $ingredients,
            'recipeInstructions' => $steps,
        ];
    }

    /**
     * @param  array<string, mixed>  $data
     */
    private function event(string $name, array $data): string
    {
        return 'event: '.$name."\n".'data: '.json_encode($data, JSON_THROW_ON_ERROR)."\n\n";
    }
}
